import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Set the backend before other matplotlib calls
from pandas_gbq import read_gbq
from google.oauth2 import service_account
from datetime import datetime
from google.cloud import bigquery
import json

# Configuration from secrets
PROJECT_ID = st.secrets["gcp"]["project_id"]
DATASET = st.secrets["gcp"]["dataset"]
TEMPERATURE_TABLE = st.secrets["gcp"]["temperature_table"]
DEMAND_TABLE = st.secrets["gcp"]["demand_table"]

# Authenticate
credentials_info = json.loads(st.secrets["gcp"]["credentials"])
credentials = service_account.Credentials.from_service_account_info(
    credentials_info,
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)


def load_data_from_bigquery(offset=0, limit=1000):
    """Load merged data from BigQuery with pagination"""
    query = f"""
    SELECT 
        DATE(temp.timestamp) as Date,
        temp.data as Temperature,
        demand.demand_value as Demand
    FROM `{PROJECT_ID}.{DATASET}.{TEMPERATURE_TABLE}` temp
    JOIN `{PROJECT_ID}.{DATASET}.{DEMAND_TABLE}` demand
    ON DATE(temp.timestamp) = DATE(demand.timestamp)
    ORDER BY Date
    LIMIT {limit} OFFSET {offset}
    """
    return read_gbq(query, project_id=PROJECT_ID, credentials=credentials)

def main():
    st.title("Temperature and Demand Over Time (BigQuery)")
    
    offset = st.number_input("Offset", min_value=0, step=1000)
    limit = st.number_input("Limit", min_value=1000, step=1000, value=1000)
    
    with st.spinner("Loading data from BigQuery..."):
        try:
            merged_data = load_data_from_bigquery(offset=offset, limit=limit)
            if merged_data.empty:
                st.warning("No data available to display.")
                return
            
            merged_data['Date'] = pd.to_datetime(merged_data['Date']).dt.date
            
            # Show raw data preview
            st.write("### Data Preview")
            st.dataframe(merged_data.head())
            
            # Create figure and primary axis
            fig, ax1 = plt.subplots(figsize=(12, 6))
            
            # Plot Temperature on primary axis
            ax1.set_xlabel('Date')
            ax1.set_ylabel('Temperature (°C)', color='blue')
            ax1.plot(merged_data['Date'], merged_data['Temperature'], 
                    color='blue', label='Temperature')
            ax1.tick_params(axis='y', labelcolor='blue')
            
            # Create secondary axis for Demand
            ax2 = ax1.twinx()
            ax2.set_ylabel('Demand (MW)', color='orange')
            ax2.plot(merged_data['Date'], merged_data['Demand'], 
                    color='orange', label='Demand')
            ax2.tick_params(axis='y', labelcolor='orange')
            
            # Add title and adjust layout
            plt.title('Temperature and Demand Over Time')
            fig.tight_layout()
            
            # Show the plot in Streamlit
            st.pyplot(fig)
            
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
