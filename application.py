import streamlit as st

# Define pages with custom titles and icons
home_page = st.Page("Kickstarter_Comparison_Engine.py", title="Kickstarter Comparison Engine")
analytics_page = st.Page("pages/1_Kickstarter_Stats.py", title="Comic Kickstarter Stats", icon=":material/analytics:")

# Initialize navigation
pg = st.navigation([home_page, analytics_page])

# Run the app structure
pg.run()