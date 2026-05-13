import streamlit as st
import polars as pl
from typing import Literal
import altair as alt

class Results():
  display_cols = ['name','blurb','goal','backers_count',
              'usd_pledged','percent_funded','launched_at','deadline',
              'prelaunch_activated','category_name','creator_name',
              'url_project']
  
  unlaunched_display_cols = ['name','blurb','goal',
                             'prelaunch_activated','category_name',
                             'creator_name','url_project']

  column_configs = {
    "name": st.column_config.TextColumn(
        "Campaign Name",
        width='medium'
    ),
    "blurb": st.column_config.TextColumn(
        "Blurb",
        width='medium'
    ),
    "goal": st.column_config.NumberColumn(
            "Goal",
            min_value=0,
            format="dollar",
        ),
    "backers_count": "Backers",
    "usd_pledged": st.column_config.NumberColumn(
            "Funds Raised",
            help="Total amount pledged in USD",
            min_value=0,
            format="dollar",
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
  
  success_scale = alt.Scale(domain=["Successful","Unsuccessful"],range=['green','red'])
  
  def __init__(self,results_df: pl.DataFrame):
    self.df = results_df
    self.create_display_df()
    self.calc_kpis()
    self.unlaunched_column_configs = {key: config for key, config in self.column_configs.items() if key in self.unlaunched_display_cols}


  def create_display_df(self):
    self.df = self.df.select(self.display_cols)\
        .with_columns(
          pl.when(pl.col("usd_pledged")>=pl.col("goal"))
          .then(pl.lit("Successful"))
          .otherwise(pl.lit("Unsuccessful"))
          .alias("Successfully Funded")
          )

  def calc_kpis(self):
    records = len(self.df)
    self.kpis = {}
    self.kpis['launches'] = self.df.select("name").unique().count().item()
    self.kpis['total_pledged'] = self.df.select(pl.sum("usd_pledged")).item()
    self.kpis['total_backer_count'] = self.df.select(pl.sum("backers_count")).item()
    self.kpis['avg_backer_count'] = self.df.select(pl.mean("backers_count")).item()
    self.kpis['avg_pledged'] = self.df.select(pl.mean("usd_pledged")).item()
    self.kpis['avg_pledge_amt'] = self.df.with_columns(
      (pl.col("usd_pledged")/pl.col("backers_count")).alias("avg_pledge")
    ).drop_nans(subset='avg_pledge').select(pl.mean("avg_pledge")).item()
    self.kpis['success_rate'] = self.df.select((pl.col("Successfully Funded") == 'Successful').sum() / records).item()
    self.kpis['avg_duration'] = self.df.with_columns(
      (pl.col("deadline")-pl.col("launched_at")).alias("duration")
      ).select(pl.mean("duration")).item()

  def display_kpi(self,metric: Literal['launches',
                                       'total_pledged',
                                       'total_backer_count'
                                       'avg_backer_count',
                                       'avg_pledged',
                                       'avg_pledge_amt',
                                       'success_rate',
                                       'avg_duration']) -> st.metric:
    
    value = self.kpis[metric]

    if 'pledge' in metric:
      display_val = f"${int(round(value,0)):,}"
    elif 'backer' in metric:
      display_val = f"{int(round(value,0)):,}"
    elif 'success' in metric:
      display_val = f"{value*100:.2f}%"
    elif 'duration' in metric:
      display_val = f"{value.days} Days"
    elif 'launches' in metric:
      display_val = f"{value:,.0f}"
    else:
      display_val = f"{value:.2f}"

    metric = metric.replace("_", " ").replace("pledged","funds raised").title()

    return st.metric(metric,display_val)
  
  def calc_range(self,var: str): 
    min_val = round(self.df.select(pl.min(var)).item() * .975,2)
    if var == 'Similarity Score':
      max_val = round(self.df.select(pl.max(var)).item() * 1.025,2)
    else:
      max_val = round(self.df.select(pl.col(var).quantile(0.95)).item())
    return [min_val, max_val]
  
  def plot_box(self,vertical: bool = False):
    
    if vertical is False:
      boxplot = alt.Chart(self.df).mark_boxplot().encode(
      alt.X("goal:Q",title="Project Goal",axis=alt.Axis(grid=False)).scale(zero=False),
      alt.Y("Successfully Funded:N", title=None,axis=alt.Axis(
        titleAngle=0,titleX=-100
        )),
      alt.Color("Successfully Funded:N",scale=self.success_scale).legend(None)
      )
    else:
      boxplot = alt.Chart(self.df).mark_boxplot().encode(
      alt.X("Successfully Funded:N"),
      alt.Y("goal:Q").scale(zero=False),
      alt.Color("Successfully Funded:N",scale=self.success_scale).legend(None)
      )      
    return st.altair_chart(boxplot.properties(title="Distribution of Kickstarter Funding Goals (USD) by Success Status"))
  
  def plot_day_of_week(self):
    day_data = self.df\
      .with_columns(pl.col("launched_at").dt.strftime("%A").alias("Day of Week"))
    
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    day_data = day_data.group_by("Day of Week").agg(pl.len().alias("# of Campaigns"),
                                                                    pl.median("usd_pledged").alias("Funds Pledged (Median)"))
    base = alt.Chart(day_data).encode(
      x = alt.X("Day of Week:O", sort=day_order, axis=alt.Axis(labelAngle=0)))

    bar = base.mark_bar().encode(
      y = alt.Y("# of Campaigns:Q", title="# of Campaigns", axis=alt.Axis(titleAngle=0,titleX=-100,grid=False)),
      color = alt.value("lightgray"),
      tooltip = ['Day of Week', '# of Campaigns']
    )

    line = base.mark_point(color='green',filled=True,size=50).encode(
      y = alt.Y("Funds Pledged (Median):Q",title = None,
                axis=None),
      tooltip = [alt.Tooltip("Funds Pledged (Median)", format='$,.0f')]
    )

    text = base.mark_text(
        align='center', 
        baseline='middle', 
        dy=-10,
        color='green'
    ).encode(
        y = alt.Y("Funds Pledged (Median):Q", title=None,axis=None),
        text = alt.Text("Funds Pledged (Median):Q", format='$,.0f'),
        tooltip = ['Day of Week', alt.Tooltip("Funds Pledged (Median)", format='$,.0f')]
    )

    final_chart = (bar + line + text).resolve_scale(y='independent').properties(title="Campaign Launches by Day: Volume (Bar) & Median Pledged (Dot)")

    return st.altair_chart(final_chart)