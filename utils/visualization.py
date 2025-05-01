import streamlit as st
import plotly.express as px
import pandas as pd

@st.cache_data(ttl=3600)
def plot_generation_bar_chart(totals, start_date, end_date):
    """Histogram of total generation by fuel type"""
    title = f"Total Generation by Fuel Type ({start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')})"
    fig = px.histogram(totals, x="Fuel Source", y="Total Generation", title=title)
    st.plotly_chart(fig)

@st.cache_data(ttl=3600)
def plot_generation_pie_chart(totals, start_date, end_date):
    """Pie chart of  generation by fuel type"""
    title = f"Proportion of Generation by Fuel Type ({start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')})"
    fig = px.pie(totals, values="Total Generation", names="Fuel Source", title=title)
    st.plotly_chart(fig)

@st.cache_data(ttl=3600)
def plot_generation_sparkline(df):
    """Data for sparklines by fuel type"""
    df_filtered = df[df['StartTime'] != 'Total'].copy()
    
    df_filtered['StartTime'] = pd.to_datetime(df_filtered['StartTime'])
    
    fuel_types = [col for col in df_filtered.columns if col not in ['StartTime', 'SettlementPeriod']]
    
    trend_data = {}
    for fuel in fuel_types:
        trend_data[fuel] = [value for value in df_filtered[fuel]]
    
    trend_df = pd.DataFrame({
        "Fuel Source": fuel_types,
        "Generation Trend": [trend_data[fuel] for fuel in fuel_types]
    })
    
    return trend_df 