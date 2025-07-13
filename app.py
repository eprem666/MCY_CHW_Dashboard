import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import streamlit as st
def load_data():
    df=pd.read_excel("CHW-Python.xlsx")
    df['Date']=pd.to_datetime(df['Date'],format='%m-%Y')
    df['Month']=df['Date'].dt.strftime('%b')
    df['Year']=df['Date'].dt.year
    return df
df=load_data()
st.sidebar.title("Filters")
selected_month=st.sidebar.selectbox("Month",sorted(df['Month'].unique()))
selected_year=st.sidebar.selectbox("Year",sorted(df['Year'].unique()))
selected_building=st.sidebar.multiselect("Building",sorted(df['Building'].unique()),default=df['Building'].unique())
selected_group=st.sidebar.multiselect("Group",sorted(df['Group'].unique()),default=df['Group'].unique())
filtered_df=df[
   (df['Month'] == selected_month) &
    (df['Year'] == selected_year) &
    (df['Building'].isin(selected_building)) &
    (df['Group'].isin(selected_group))
]             
st.markdown("<h1 style='color:black; font-family:Calibri; font-size:24px;'>CHW Consumption - [Sep 2023 - Jun 2025]</h1>", unsafe_allow_html=True)
monthly_total = df.groupby('Date')['Consumption'].sum().reset_index()
fig1 = px.bar(monthly_total, x='Date', y='Consumption', color='Date', title="Monthly CHW Consumption")
fig1.update_traces(text=monthly_total['Consumption'], textposition='outside')
fig1.update_layout(xaxis_title='Month', yaxis_title='Total Consumption', width=1000, height=400)
st.plotly_chart(fig1)
cumulative_df = monthly_total[monthly_total['Date'] >= datetime(2024, 1, 1)].copy()
cumulative_df['Cumulative'] = cumulative_df['Consumption'].cumsum()
col1, col2 = st.columns(2)
fig2 = px.line(cumulative_df, x='Date', y='Cumulative', title='CHW-Consumption - Cumulative', markers=True)
fig2.update_layout(height=400)
col1.plotly_chart(fig2)
current_date = datetime.strptime(f"{selected_month}-{selected_year}", "%b-%Y")
prev_date = current_date - pd.DateOffset(months=1)
group_data = df[df['Date'].isin([prev_date, current_date])]
pivot = group_data.groupby(['Date', 'Group'])['Consumption'].sum().unstack().fillna(0)
if current_date in pivot.index and prev_date in pivot.index:
   diff = ((pivot.loc[current_date] - pivot.loc[prev_date]) / pivot.loc[prev_date]) * 100
else:
     diff = pd.Series([0, 0, 0], index=['Residential', 'Commercial', 'Newton academy'])
for grp in ['Residential', 'Commercial', 'Newton academy']:
     val = round(diff.get(grp, 0), 2)
     fig_donut = go.Figure(go.Pie(
         values=[abs(val), 100 - abs(val)],
        labels=['Change', 'Remaining'],
        hole=0.6,
        marker_colors=['#0074D9', '#DDDDDD'],
        textinfo='none'
     ))
     fig_donut.update_layout(title=f"{grp}: {val:+.2f}%", height=250, width=250)
col2.plotly_chart(fig_donut)
this_total = filtered_df['Consumption'].sum()
prev_total = df[
    (df['Date'] == prev_date) &
    (df['Building'].isin(selected_building)) &
    (df['Group'].isin(selected_group))
]['Consumption'].sum()
overall_diff = ((this_total - prev_total) / prev_total) * 100 if prev_total != 0 else 0
gauge_color = "green" if overall_diff < 0 else "yellow" if overall_diff <= 10 else "red"
fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=overall_diff,
    title={'text': "Overall % Difference"},
    gauge={
        'axis': {'range': [-100, 100]},
        'bar': {'color': gauge_color},
        'steps':[
            {'range': [-100, 0], 'color': "lightgreen"},
            {'range': [0, 10], 'color': "yellow"},
            {'range': [10, 100], 'color': "red"}
        ]
    }
))
col2.plotly_chart(fig_gauge)