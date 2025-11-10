import streamlit as st
import app_reference as ref
from results import Results
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
    cluster_start = datetime.datetime.now()
    st.write(f"Similarity search started at: {cluster_start}")
    sim_search.find_nearest_neighbors()
    cluster_end = datetime.datetime.now()
    st.write(f"Similarity search completed in: {cluster_end-cluster_start}")
    sim_search.retrieve_results()
    end = datetime.datetime.now()
    st.write(f"Total Runtime: {end-start}")

    results = Results(sim_search.final_results)
    kpis_1,kpis_2,kpis_3,kpis_4 = st.columns(4)
    with kpis_1:
        results.display_kpi('avg_backers')
    with kpis_2:
        results.display_kpi('avg_pledged')
    with kpis_3:
        results.display_kpi('avg_pledge_amt')
    with kpis_4:
        results.display_kpi('success_rate')
    st.divider()
    st.dataframe(
        results.df,
        column_config = results.column_configs,
        hide_index = True
        )