import streamlit as st

# Define pages with custom titles and icons
home_page = st.Page("Kickstarter_Comparison_Engine.py", title="Kickstarter Comparison Engine", icon="🔍")
analytics_page = st.Page("pages/1_Kickstarter_Stats.py", title="Comic Kickstarter Stats", icon="📊")
model_page = st.Page("pages/2_Kickstarter_Model.py", title="Comic Campaign Forecaster", icon="🎯")

# Initialize navigation
pg = st.navigation([home_page, analytics_page, model_page])

# Run the app structure
pg.run()