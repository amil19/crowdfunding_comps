import streamlit as st
import polars as pl
from typing import Literal

class Results():
  display_cols = ['Similarity Score','name','blurb','goal','backers_count',
              'usd_pledged','percent_funded','launched_at','deadline',
              'prelaunch_activated','category_name','creator_name',
              'url_project']
  
  column_configs = {
    "Similarity Score": st.column_config.NumberColumn(
            "Similarity Score",
            format="%.1f",
        ),
    "name": "Campaign Name",
    "blurb": st.column_config.TextColumn(
        "Blurb",
        width='medium'
    ),
    "goal": st.column_config.NumberColumn(
            "Goal",
            min_value=0,
            format="$%d",
        ),
    "backers_count": "Backers",
    "usd_pledged": st.column_config.NumberColumn(
            "Funds Raised",
            help="Total amount pledged in USD",
            min_value=0,
            format="$%.2f",
        ),
    "percent_funded": st.column_config.NumberColumn(
            "Pct Funded",
            help="Percentage of Goal Funded",
            min_value=0,
            format="%.2f%%",
        ),
    "launched_at":st.column_config.DatetimeColumn(
            "Launch Date",
            format="MM/DD/YYYY, h:mm a"),
    "deadline": st.column_config.DatetimeColumn(
            "End Date",
            format="MM/DD/YYYY, h:mm a"),
    "category_name": "Category",
    "prelaunch_activated": st.column_config.CheckboxColumn(
            "Prelaunch Activated?",
            default=False,
        ),
    "creator_name": "Creator",
    "url_project": st.column_config.LinkColumn("Project Link",display_text = "Link")}
  
  
  
  def __init__(self,results_df: pl.DataFrame):
    self.df = results_df
    self.create_display_df()
    self.calc_kpis()

  def create_display_df(self):
    self.df = self.df.select(self.display_cols)

  def calc_kpis(self):
    records = len(self.df)
    self.kpis = {}
    self.kpis['avg_backers'] = self.df.select(pl.mean("backers_count")).item()
    self.kpis['avg_pledged'] = self.df.select(pl.mean("usd_pledged")).item()

    self.kpis['avg_pledge_amt'] = self.df.with_columns(
      (pl.col("usd_pledged")/pl.col("backers_count")).alias("avg_pledge")
    ).select(pl.mean("avg_pledge")).item()
    self.kpis['success_rate'] = self.df.filter(pl.col("usd_pledged")>=pl.col("goal")).select(pl.len() / records).item()

  def display_kpi(self,metric: Literal['avg_backers',
                                       'avg_pledged',
                                       'avg_pledge_amt',
                                       'success_rate']) -> st.metric:
    
    value = self.kpis[metric]

    if 'avg_pledge' in metric:
      display_val = f"${int(round(value,0)):,}"
    elif 'avg_backers' in metric:
      display_val = f"{int(round(value,0)):,}"
    else:
      display_val = f"{value*100:.2f}%"

    metric = metric.replace("_", " ").title()

    return st.metric(metric,display_val)