# from embeddings import Embeddings
from embeddings import Embeddings
import polars as pl
import duckdb
import app_reference as ref
import streamlit as st
import faiss
import numpy as np

from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

class SimilaritySearch():
    
    def __init__(self,title: str,blurb: str,goal: float,category: str,subcategory: str,n_comps: int):
        self.title = title
        self.blurb = blurb
        self.goal = goal
        self.category = category
        self.subcategory = subcategory
        self.n_comps = n_comps
        self.query_df = pl.DataFrame({'id': [0],
                                      'name': [self.title],
                                      'blurb': [self.blurb],
                                      'goal': [self.goal],
                                      'category_parent_name': [self.category],
                                      'category_name': [self.subcategory]
                                      }).cast({'id': pl.Int64, 'goal': pl.Float32})

    def load_data(self):
        query = f"Select {','.join(ref.ks_table_cols)} from {ref.ks_table} where category_parent_name = '{self.category}' limit 1000"
        with duckdb.connect(ref.ks_db, read_only=True) as conn:
            self.lf = conn.sql(query).pl().lazy()

    def prep_data(self):
        self.create_embeddings()
        self.convert_to_pandas()
        self.create_preprocessor()
        self.create_data_for_clustering()

    def create_embeddings(self):
        self.embed = Embeddings(self.lf,'id',ref.Model_Cols.embedding_columns)
        self.model_df = self.embed.transform()

    def create_data_for_clustering(self):
        self.data_for_clustering = self.preprocessor.fit_transform(self.model_df)
        X_combined = np.hstack((self.data_for_clustering, self.embed.embeddings))

        # X_combined is now a clean N x (C + D) NumPy array, ready for Faiss
        self.data_for_clustering = X_combined.astype(np.float32)


    def convert_to_pandas(self):
        self.model_df = self.model_df.drop(['name','blurb','cols_to_embed','embeddings']).to_pandas()
        self.model_df = self.model_df.set_index('id')
    
    def create_preprocessor(self):
        # 2) Create Preprocessor for Pipeline
        self.preprocessor = ColumnTransformer(
            transformers=[
                ("numerical", StandardScaler(), ref.Model_Cols.numeric_columns),
                ("categorical",OneHotEncoder(),ref.Model_Cols.categorical)],remainder='passthrough'
        )

    def setup_faiss(self):
        self.get_dimensions()
        self.build_faiss_index()
        self.add_vectors_to_index()
        self.create_query_vector()

    def get_dimensions(self):
        self.dimensions = len(self.data_for_clustering[0])

    def build_faiss_index(self):
        self.faiss_index = faiss.IndexFlatL2(self.dimensions)

    def add_vectors_to_index(self):
        self.faiss_index.add(self.data_for_clustering)

    def create_query_vector(self):
        self.embed_inputs = Embeddings(self.query_df,'id',ref.Model_Cols.embedding_columns)
        self.embed_inputs.create_documents()
        self.query_df_updated = self.embed_inputs.transform()
        self.query_embeddings = self.embed.model.encode(self.embed_inputs.documents, convert_to_numpy=True).astype(np.float32)
        self.query_df_updated = self.query_df_updated.drop(['name','blurb','cols_to_embed','embeddings']).to_pandas()
        self.query_df_updated = self.query_df_updated.set_index('id')

        self.query_df_transformed = self.preprocessor.transform(self.query_df_updated)
        self.query_vector = np.hstack((self.query_df_transformed, self.query_embeddings))

        # X_combined is now a clean N x (C + D) NumPy array, ready for Faiss
        self.query_vector = self.query_vector.astype(np.float32)

    def find_nearest_neighbors(self,k: int=None):
        if k is None:
            k = self.n_comps
        D, I = self.faiss_index.search(self.query_vector,k)
        self.D = D
        self.I = I
    
    def retrieve_results(self):
        # Initialize lists to hold the results (list of lists)
        all_ids = []
        all_distances = []

        # Outer loop: Iterates over each query vector (row)
        for i_row, d_row in zip(self.I, self.D):
            
            # Initialize lists for the k neighbors of the current query vector
            current_ids = []
            current_distances = []
            
            # Inner loop: Iterates over each neighbor index within the current row
            for index_pos, distance_val in zip(i_row, d_row):
                
                # 1. Retrieve the single ID label using the single index position
                # This returns a numpy.int64 or a native Python int if your index is that type
                id_value = self.model_df.index[index_pos]
                
                # 2. Safely cast to native Python int() if necessary
                current_ids.append(int(id_value)) 
                current_distances.append(distance_val)
            
            # Append the results for the current query vector to the final list
            all_ids.append(current_ids)
            all_distances.append(current_distances)
            
        self.ids = [item for sublist in all_ids for item in sublist]
        self.distances = [item for sublist in all_distances for item in sublist]

        results_df = pl.DataFrame({'id': self.ids,'distance': self.distances}).cast({'id': pl.Int64}).lazy()
        combined_results_df = results_df.join(self.lf,on='id',how='inner')
        st.write(combined_results_df.collect().sort('distance'))
