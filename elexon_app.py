import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import datetime
from google.oauth2 import service_account
import pandas_gbq


@st.cache_data
def load_data():
    creds = st.secrets["gcp_service_account"]
    credentials = service_account.Credentials.from_service_account_info(creds)

    sql = """
        SELECT *
        FROM `sipa-adv-c-arshiya-ijaz.elexon_energy.generation_data`
        ORDER BY StartTime DESC
        LIMIT 100
    """
    return pandas_gbq.read_gbq(sql, credentials=credentials)

def get_generation_data(api_url):
  api_response = requests.get(api_url)
  api_response = api_response.json()
  generation_data = api_response['data']
  return generation_data

def flatten_generation_data(original):
  ''' Flattens/ fixes the data formatting and converts it into a pd df'''
  result = {
      'StartTime': original['startTime'],
      'SettlementPeriod':original['settlementPeriod'],
  }

  for element in original['data']:
    psr_type = element['psrType']
    result[psr_type] = element['quantity']

  return result

def process_data(generation_data):
  df = pd.DataFrame(map(flatten_generation_data, generation_data))
  return df

def calculate_totals(df):
    """Calculates total electricity generation by fuel sourc for the time period the user selected"""
    total_by_source = df.iloc[:, 1:].sum()
    total_row = pd.DataFrame([['Total'] + total_by_source.tolist()], columns=df.columns)
    df = pd.concat([df, total_row], ignore_index=True)
    totals = df.iloc[:, 1:].sum().reset_index()
    totals.columns = ["Fuel Source", "Total Generation"]
    return df, totals

def plot_generation_bar_chart(totals, start_date, end_date):
    """Histogram of total generation by fuel type"""
    title = f"Total Generation by Fuel Type ({start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')})"
    fig = px.histogram(totals, x="Fuel Source", y="Total Generation", title=title)
    st.plotly_chart(fig)

def plot_generation_pie_chart(totals, start_date, end_date):
    """Pie chart of  generation by fuel type"""
    title = f"Proportion of Generation by Fuel Type ({start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')})"
    fig = px.pie(totals, values="Total Generation", names="Fuel Source", title=title)
    st.plotly_chart(fig)

def display_top_fuel_metrics(totals):
    """Streamlit metrics for the top 3 fuel types by generation"""
    sorted_totals = totals.sort_values("Total Generation", ascending=False)
    top_3_fuels = sorted_totals.head(3)
    
    st.write("### Top Fuel Sources (MW)")
    
    for _, row in top_3_fuels.iterrows():
        fuel_name = row["Fuel Source"]
        generation_value = row["Total Generation"]
        
        formatted_value = f"{generation_value / 1_000_000:.2f}M"
        
        st.metric(
            label=f"{fuel_name}",
            value=formatted_value)

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

def main():
    st.title("Elexon Energy - UK Electricity Data")
    st.write("Project Team: Arshiya Sawhney and Ijaz Ahmed Khan")
    
    st.sidebar.header("Select Dates")
    
    default_start_date = datetime.date(2025, 1, 1)
    default_end_date = datetime.date(2025, 2, 1)
    
    start_date = st.sidebar.date_input("Start Date", default_start_date)
    end_date = st.sidebar.date_input("End Date", default_end_date)
    
    if start_date > end_date:
        st.error("Error: End date must be after start date.")
        return
    
    #api_url = f"https://data.elexon.co.uk/bmrs/api/v1/generation/actual/per-type?from={start_date}&to={end_date}&settlementPeriodFrom=1&settlementPeriodTo=48&format=json"
    #generation_data = get_generation_data(api_url)
    #df = process_data(generation_data)
    
    df = load_data()

    df, totals = calculate_totals(df)

    plot_generation_bar_chart(totals, start_date, end_date)
    
    display_top_fuel_metrics(totals)
    
    plot_generation_pie_chart(totals, start_date, end_date)
    
    st.write("### Generation Trends by Fuel Type")
    
    trend_df = plot_generation_sparkline(df)
    
    st.dataframe(
        trend_df,
        column_config={
            "Fuel Source": st.column_config.TextColumn("Fuel Type"),
            "Generation Trend": st.column_config.LineChartColumn(
                f"Generation by Settlement Period (MW) ({start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')})",
                width="large",
                help="Actual electricity generation at each settlement period (MW)"
            )
        },
        hide_index=True
    )
      
    st.write("Data Summary/ Structure:")
    st.dataframe(df.head())

if __name__ == "__main__":
    main()


