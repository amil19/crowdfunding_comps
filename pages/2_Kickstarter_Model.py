import streamlit as st
import app_reference as ref
import duckdb
from rich.console import Console
import pandas as pd
import numpy as np
import lightgbm as lgb


st.set_page_config(layout="wide")

st.markdown(ref.css,unsafe_allow_html=True)

st.header("Comic Kickstarter Campaign Forecaster")


@st.cache_resource
def load_model():
    conn_str = f"{st.secrets['DUCKDB']}?motherduck_token={st.secrets['DUCKDB_TOKEN']}"
    with duckdb.connect(conn_str) as conn:
        model_query = """SELECT model_text 
        FROM model_registry WHERE model_id = 'ks_comic_forecast_model_v1'
        """
        model_text = conn.execute(model_query).fetchone()[0]
        model = lgb.Booster(model_str=model_text)
    Console().log("[green] Successfully loaded model")
    return model

model = load_model()

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df['percent_funded'] = np.where(df['goal']>0, df['usd_pledged'] / df['goal'], 0)
    df['campaign_progress'] = np.where(df['campaign_duration'] > 0, df['campaign_day'] / df['campaign_duration'], 0)
    df['avg_pledge_amount'] = np.where(df['backers_count'] > 0, df['usd_pledged'] / df['backers_count'], 0)
    df['avg_backers_per_day'] = np.where(df['campaign_day'] > 0, df['backers_count'] / df['campaign_day'], 0)
    
    return df.drop('campaign_duration', axis=1)

days = {'Sunday': 0, 'Monday': 1, 'Tuesday': 2, 'Wednesday': 3,
        'Thursday': 4, 'Friday': 5, 'Saturday': 6}

input_model = {}

st.subheader("Campaign Progress")
prog1, prog2, prog3 = st.columns(3)
with prog1:
    input_model['usd_pledged'] = st.number_input(label='Current Amount Pledged ($)', min_value=0.0)
with prog2:
    input_model['backers_count'] = st.number_input(label='Current # of Backers', min_value=0)
with prog3:
    input_model['campaign_day'] = st.number_input(label='Current Campaign Day', min_value=1, max_value=70)

st.subheader("Campaign Details")
meta1, meta2, meta3 = st.columns(3)
with meta1:
    input_model['goal'] = st.number_input(label='Funding Goal (in USD)', min_value=0.0)
with meta2:
    input_model['campaign_duration'] = st.number_input(label='Campaign Length (in Days)', min_value=1, max_value=70)
with meta3:
    input_model['creator_campaign_count'] = st.number_input(label='# of Previous Launches by Creator', min_value=0)
day_col1, day_col2 = st.columns(2)
with day_col1:
    input_model['launch_weekday'] = days[st.selectbox(label='Launch Day of Week', options=days)]
with day_col2:
    input_model['end_weekday'] = days[st.selectbox(label='Deadline Day of Week', options=days)]

select_order = ['launch_weekday',
 'end_weekday',
 'usd_pledged',
 'goal',
 'backers_count',
 'percent_funded',
 'creator_campaign_count',
 'campaign_day',
 'campaign_progress',
 'avg_pledge_amount',
 'avg_backers_per_day']


if st.button("Generate prediction"):
    with st.spinner("Calculating forecast..."):
        # Convert input dict to DataFrame
        df = pd.DataFrame([input_model])
        
        # Apply engineered features
        df = engineer_features(df)[select_order]

        # Generate prediction
        prediction = model.predict(df)[0]

    st.success("Prediction successfuly generated")
    st.metric('Projected Final Pledge Amount: ', value=f'${int(prediction):,}')