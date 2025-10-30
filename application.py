import streamlit as st
import app_reference as ref
from sim_search import SimilaritySearch
import datetime

st.header("Kickstarter Comparison Engine")

st.write("""Enter a campaign title, description, category, goal, duration, and region and get the top n similar campaigns, metrics, and benchmarks
""")
st.subheader("Enter info for basis campaign below")

input_col1,input_col2 = st.columns(2)

with input_col1:
    campaign_title = st.text_input("Campaign Title", key="campaign_title")
    blurb = st.text_input("Blurb",key='blurb')
    goal = st.number_input("Funding Goal",key='goal')

with input_col2:
    category_parent = st.selectbox("Category", options=ref.parent_categories,index=None,key='category_parent')
    if category_parent:
        subcats = ref.categories[category_parent]
        subcats.sort()
        category_name = st.selectbox("Subcategory", options=subcats,key='category_name')
        number_of_comps = round(st.number_input("Number of similar campaigns you want to see",min_value=2,max_value=50,key='number_of_comps'),0)
run = False
try:
    if number_of_comps:
        run = st.button("Run similarity search")
except NameError:
    pass

if run:
    sim_search = SimilaritySearch(campaign_title,blurb,goal,category_parent,category_name,number_of_comps)
    start = datetime.datetime.now()
    st.write(f"Starting engine at: {start}")
    st.write("Loading Kickstarter Data")
    sim_search.load_data()
    st.write("Preparing Data for Clustering")
    sim_search.prep_data()
    sim_search.setup_faiss()
    st.write("Cluster Model Ready")
    sim_search.find_nearest_neighbors()
    sim_search.retrieve_results()
    end = datetime.datetime.now()
    st.write(f"Runtime: {end-start}")