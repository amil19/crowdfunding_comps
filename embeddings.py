from sentence_transformers import SentenceTransformer
import polars as pl
import numpy as np

class Embeddings():

    def __init__(self,df: pl.DataFrame | pl.LazyFrame, cols_to_embed: list[str]):
        """Initializes class to create embeddings.

        Args:
            df (pl.DataFrame | pl.LazyFrame): DataFrame containing columns to embed.
            cols_to_embed (list[str]): Name(s) of columns to embed.
        """
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.df = df
        self.cols_to_embed = [pl.col(col) for col in cols_to_embed]

    def create_documents(self):
        """Creates documents that are fed to embedding model.
        """
        print("Concatenating columns")
        self.df = self.df.with_columns(pl.concat_str(self.cols_to_embed).alias('cols_to_embed'))

        if isinstance(self.df,pl.LazyFrame):
            self.df = self.df.collect()
        print("Turning concactenated column to a list")
        self.documents = self.df.select("cols_to_embed").to_series().to_list()

    def transform(self) -> pl.DataFrame:
        """Creates embeddings and adds them to the original DataFrame.

        Returns:
            pl.DataFrame: Original DataFrame with additional 'embeddings' column.
        """
        self.create_documents()
        print("Created documents")
        self.embeddings = self.model.encode(self.documents, convert_to_numpy=True).astype(np.float32)
        print("Created embeddings")

        self.df = self.df.with_columns(pl.Series(list(self.embeddings)).alias("embeddings"))
        print("Added embeddings to DataFrame")
        
        return self.df