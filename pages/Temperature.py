import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Set the backend before other matplotlib calls
from pandas_gbq import read_gbq
from google.oauth2 import service_account
#from datetime import datetime
#from google.cloud import bigquery
import json
import time

# Configuration from secrets
PROJECT_ID = st.secrets["gcp_service_account"]["project_id"]
DATASET = "elexon_energy"
TEMPERATURE_TABLE = "temperature"
DEMAND_TABLE = "demand"

# Authenticate
credentials_info = st.secrets["gcp_service_account"]
credentials = service_account.Credentials.from_service_account_info(
    credentials_info,
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)

# Cacheing bigquery data
@st.cache_data(show_spinner=False)
def load_data_from_bigquery(offset=0, limit=1000, start_date=None, end_date=None):
    """Load merged data from BigQuery with pagination"""

    if start_date and end_date:
        where_clause = f"WHERE DATE(temp.timestamp) BETWEEN '{start_date}' AND '{end_date}'"
    else:
        where_clause = ""
    # SQL query to select and join data from temperature and demand tables    
    query = f"""
    SELECT 
        DATE(temp.timestamp) as Date,
        temp.data as Temperature,
        demand.demand_value as Demand
    FROM `{PROJECT_ID}.{DATASET}.{TEMPERATURE_TABLE}` temp
    JOIN `{PROJECT_ID}.{DATASET}.{DEMAND_TABLE}` demand
    ON DATE(temp.timestamp) = DATE(demand.timestamp)
    {where_clause}
    ORDER BY Date
    LIMIT {limit} OFFSET {offset}
    """
    return read_gbq(query, project_id=PROJECT_ID, credentials=credentials)

# Cached date processing
@st.cache_data(show_spinner=False)
def process_dates(df):
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    return df


# Plotting graphs Temperature on Demand for electricity
def plot_temp_demand(data):
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Plot Temperature on primary axis
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Temperature (°C)', color='blue')
    ax1.plot(data['Date'], data['Temperature'], color='blue', label='Temperature')
    ax1.tick_params(axis='y', labelcolor='blue')

    # Create secondary axis for Demand
    ax2 = ax1.twinx()
    ax2.set_ylabel('Demand (MW)', color='orange')
    ax2.plot(data['Date'], data['Demand'], color='orange', label='Demand')
    ax2.tick_params(axis='y', labelcolor='orange')

    plt.title('Temperature and Demand Over Time')
    fig.tight_layout()
    return fig

def main():
    page_start = time.time()

    st.title("Temperature and Demand Over Time (BigQuery)")
    st.set_page_config(page_title="Temperature-Demand prediction", layout="wide")
    # Pagination input
    offset = st.number_input("Offset", min_value=0, step=1000)
    limit = st.number_input("Limit", min_value=100, step=100, value=1000)

    # Date range input
    date_range = st.date_input("Filter by Date Range (optional)", [])
    start_date, end_date = None, None
    if date_range and len(date_range) == 2:
        start_date = date_range[0].isoformat()
        end_date = date_range[1].isoformat()
    
    with st.spinner("Loading data from BigQuery..."):
        try:
            start_time = time.time()
            merged_data = load_data_from_bigquery(
                offset=offset, limit=limit, start_date=start_date, end_date=end_date
            )

            load_duration = time.time() - start_time
            st.write(f"⏱ Data loaded in {load_duration:.2f} seconds")

            if merged_data.empty:
                st.warning("No data available to display.")
                return

            # Process dates
            merged_data = process_dates(merged_data)
            #merged_data['Date'] = pd.to_datetime(merged_data['Date']).dt.date

            # Preview data
            st.write("### Data Preview")
            st.dataframe(merged_data.head())

            # Plot
            # fig = plot_temp_demand(merged_data)
            # st.pyplot(fig)
            with st.expander("Show Temperature-Demand Plot"):
                fig = plot_temp_demand(merged_data)
                st.pyplot(fig)

            page_end = time.time()
            st.write(f" Total page load time: {page_end - page_start:.2f} seconds")

            # Feedback streamlit

            # if load_duration > 2:
            #     st.error(" Page load exceeded 2 seconds. Consider filtering or increasing efficiency.")
            # else:
            #     st.success(" App is performant!")

            
        except Exception as e:
            st.error(f"Failed to load data: {str(e)}")
            st.info("""
            Please ensure:
            1. Tables exist in BigQuery
            2. Service account has proper permissions
            3. Tables contain data
            """)

if __name__ == "__main__":
    main()

## weather data

# weather_api"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/united%20kingdom/2024-01-01/2024-12-31?unitGroup=us&key=YSMAWYWAAQUCN4STA4XFW68XA&contentType=json"
# weather_data = temperature_data.fetch_temperature_data(weather_api)
