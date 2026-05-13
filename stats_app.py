import streamlit as st
import app_reference as ref
from stats_results import Results
# from sim_search import SimilaritySearch
import duckdb
from rich.console import Console
import polars as pl
import altair as alt
#import datetime

st.set_page_config(layout="wide")

st.markdown(ref.css,unsafe_allow_html=True)

st.header("Comic Kickstarter Stats")

st.write("""
---
""")
st.subheader("View Campaigns by Creator")

@st.cache_data
def load_data():
    """Loads Kickstarter campaigns from database.
    """
    table_cols = ref.ks_table_cols
    table_cols.remove('embeddings')
    query = f"""
    Select distinct {','.join(table_cols+ref.ks_kpi_cols)}
    ,case when launched_at < '1971-01-01' then 0 else 1 end as Launched
    from {ref.ks_table} 
    where category_parent_name = 'Comics' 
    and embeddings IS NOT NULL
    order by launched_at desc"""
    with duckdb.connect(f"{st.secrets['DUCKDB']}?motherduck_token={st.secrets['DUCKDB_TOKEN']}") as conn:
    #with duckdb.connect(ref.ks_db, read_only=True) as conn:
        return conn.sql(query).pl().unique(subset=['id'],keep='first').lazy()

if 'lf' not in st.session_state:
    st.session_state['lf'] = load_data()
    Console().log("[green] Successfully loaded Kickstarter data")

@st.fragment
def set_creator_list():
    creators = st.session_state['lf'].select("creator_name").unique().sort("creator_name")\
        .collect().to_series().to_list()
    Console().log("Creator List set")    
    return creators

if 'creators' not in st.session_state:
    st.session_state['creators'] = set_creator_list()

creator_name = st.selectbox("Select Creator",options=st.session_state['creators'],index=None)

@st.fragment
def filter_data(creator) -> pl.DataFrame:
    return st.session_state['lf'].filter(pl.col("creator_name")==creator)\
        .sort(["Launched","launched_at"],descending=[False,True]).collect()

if creator_name:
    creator_df = filter_data(creator_name)
    unlaunched = creator_df.filter(pl.col("Launched")==0)
    unlaunched = Results(unlaunched)
    launched_df = creator_df.filter(pl.col("Launched")==1)
    launched_df = launched_df.sort("launched_at",descending=True)
    results = Results(launched_df)
    st.subheader("Campaign Stats")

    kpis_1_1,kpis_1_2,kpis_1_3,kpis_1_4 = st.columns(4)
    with kpis_1_1:
        results.display_kpi('launches')
    with kpis_1_2:
        results.display_kpi('total_pledged')
    with kpis_1_3:
        results.display_kpi('total_backer_count')
    with kpis_1_4:
        results.display_kpi('success_rate')
    kpis_2_1,kpis_2_2,kpis_2_3,kpis_2_4 = st.columns(4)
    with kpis_2_1:
        results.display_kpi('avg_pledged')
    with kpis_2_2:
        results.display_kpi('avg_backer_count')
    with kpis_2_3:    
        results.display_kpi('avg_pledge_amt')
    with kpis_2_4:
        results.display_kpi('avg_duration')
        
    if len(unlaunched.df) > 0:
        st.subheader("Pending Campaigns")
        st.dataframe(
        unlaunched.df.select(unlaunched.unlaunched_display_cols),
        column_config = unlaunched.unlaunched_column_configs,
        hide_index = True,
        row_height=100)

    st.subheader("Launched Campaigns")

    tab_1,tab_2,tab_3 = st.tabs(["Funds Raised","Funding Goals","Launch Day Analysis"])
    #tab_1,tab_2,tab_3 = st.columns(3)
    with tab_1:
        plot_df = launched_df.with_columns(pl.col("launched_at").dt.strftime("%Y-%m"))
        base = alt.Chart(plot_df).encode(
            x=alt.X('launched_at:O', title='Launch Date',axis=alt.Axis(labelAngle=0))#axis=alt.Axis(format='%m-%d-%Y'))
        )

        lines = base.mark_bar().encode(
            y=alt.Y("usd_pledged:Q",title = 'Funds Raised',axis=alt.Axis(format='$,.0f',titleAngle=0,titlePadding=50))
            ,tooltip = [
                alt.Tooltip('name', title='Campaign:')
            ]
            ,color=alt.Color('name:N',legend=None)
        )

        lines = lines.configure_axis(grid=False).configure_view(stroke=None)

        st.altair_chart(lines)
    with tab_2:
        #st.subheader("Goal Benchmarking")
        results.plot_box()
    with tab_3:
        #st.subheader("Launch Day Analysis")
        results.plot_day_of_week()
    st.subheader("Launched Campaign Table")
    st.dataframe(
    results.df,
    column_config = results.column_configs,
    hide_index = True,
    row_height=100)