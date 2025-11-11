import streamlit as st
import app_reference as ref
from results import Results
from sim_search import SimilaritySearch
import datetime

st.set_page_config(layout="wide")

st.markdown(ref.css,unsafe_allow_html=True)

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
        number_of_comps = round(st.number_input("Number of similar campaigns you want to see",min_value=2,max_value=150,key='number_of_comps'),0)
run = False
try:
    if number_of_comps:
        run = st.button("Run similarity search")
except NameError:
    pass

if run:
    sim_search = SimilaritySearch(campaign_title,blurb,goal,category_parent,category_name,number_of_comps)
    start = datetime.datetime.now()
    progress_bar = st.progress(0, text=f"Starting engine at: {start}")
    status_text = st.empty()

    status_text.write("Loading Kickstarter Data")
    sim_search.load_data()
    progress_bar.progress(50, text="Loading Data (Step: 1/3)")
    status_text.write("Preparing Data for Clustering")
    sim_search.prep_data()
    sim_search.setup_faiss()
    progress_bar.progress(90, text="Preparing Data for Clustering (Step: 2/3)")
    cluster_start = datetime.datetime.now()
    progress_bar.progress(90, text="Searching for Similar Campaigns (3/3)")
    sim_search.find_nearest_neighbors()
    cluster_end = datetime.datetime.now()

    progress_bar.progress(100, text="Completed!")
    sim_search.retrieve_results()
    end = datetime.datetime.now()

    status_text.write(f"Total Runtime: {end-start}")
    st.success(f"Similarity search completed in: {cluster_end-cluster_start}")

    results = Results(sim_search.final_results)

    st.subheader("Key Performance Indicators (KPIs) for Similar Campaigns")

    kpis_1,kpis_2,kpis_3,kpis_4,kpis_5 = st.columns(5)
    with kpis_1:
        results.display_kpi('avg_backers')
    with kpis_2:
        results.display_kpi('avg_pledged')
    with kpis_3:
        results.display_kpi('avg_pledge_amt')
    with kpis_4:
        results.display_kpi('avg_duration')
    with kpis_5:    
        results.display_kpi('success_rate')



    tab_1,tab_2,tab_3 = st.tabs(["Goal Benchmarking","Similarity vs Performance","Launch Day Analysis"])
    #tab_1,tab_2,tab_3 = st.columns(3)
    with tab_1:
        #st.subheader("Goal Benchmarking")
        results.plot_box()
    with tab_2:
        #st.subheader("Similarity vs Performance")
        results.plot_similarity()
    with tab_3:
        #st.subheader("Launch Day Analysis")
        results.plot_day_of_week()
    st.subheader("Detailed Comparison Table")
    st.dataframe(
    results.df,
    column_config = results.column_configs,
    hide_index = True,
    row_height=100)