import pandas as pd
from pandas_gbq import to_gbq, read_gbq
import requests
from google.oauth2 import service_account
# from datetime import datetime
from datetime import datetime
import json
import os

# configuration

PROJECT_ID = "sipa-adv-c-arshiya-ijaz"
DATASET = "elexon_energy"
TABLE_TEMPERATURE = "temperature"
TABLE_DEMAND = "demand"
WEATHER_TABLE = "weather"
MERGED_TABLE = "merged_data"
FULL_TABLE_MERGED = f"{PROJECT_ID}.{DATASET}.{MERGED_TABLE}"
FULL_TABLE_WEATHER = f"{PROJECT_ID}.{DATASET}.{WEATHER_TABLE}"
FULL_TABLE_TEMPERATURE = f"{PROJECT_ID}.{DATASET}.{TABLE_TEMPERATURE}"
FULL_TABLE_DEMAND = f"{PROJECT_ID}.{DATASET}.{TABLE_DEMAND}"
SCOPES = ['https://www.googleapis.com/auth/cloud-platform',
        'https://www.googleapis.com/auth/drive'
]



# === AUTHENTICATION ===
def get_bq_credentials():
    """Get BigQuery Credentials from environment or local JSON."""
    bq_credentials_env = os.environ.get('ELEXON_SECRETS_AS')
    if bq_credentials_env:
        # From environment (GitHub Actions)
        bq_credentials = json.loads(bq_credentials_env)
    else:
    # Fallback options
        try:
            import streamlit as st
            bq_credentials = st.secrets["gcp_service_account"]  # Streamlit Cloud
        except Exception:
            try:
                with open("key.json") as f:  # Local key file
                    bq_credentials = json.load(f)
            except Exception:
                raise Exception("No credentials found! Either set ELEXON_SECRETS_AS env variable or add a key file or streamlit secrets.")

    credentials = service_account.Credentials.from_service_account_info(
        bq_credentials, scopes=SCOPES
    )
    return credentials

def check_table_exists(table_name, credentials):
    """Check if a table exists in BigQuery"""
    query = f"""
    SELECT table_name 
    FROM `{PROJECT_ID}.{DATASET}.INFORMATION_SCHEMA.TABLES`
    WHERE table_name = '{table_name}'
    """
    try:
        df = read_gbq(query, project_id=PROJECT_ID, credentials=credentials)
        return not df.empty
    except Exception as e:
        print(f"Error checking table existence: {str(e)}")
        return False

# Create a new table with appropriate schema
def create_table(full_table_name, credentials, is_demand=False, is_weather=False):
    """Create a new table with appropriate schema"""
    if is_weather:
        schema = [
            {"name": "date", "type": "DATE"},
            {"name": "temp", "type": "FLOAT"},
            {"name": "humidity", "type": "FLOAT"},
            {"name": "precip", "type": "FLOAT"},
            {"name": "windspeed", "type": "FLOAT"},
            {"name": "cloudcover", "type": "FLOAT"}
        ]
        df_empty = pd.DataFrame(columns=[col["name"] for col in schema])
    elif is_demand:
        schema = [
            {"name": "timestamp", "type": "TIMESTAMP"},
            {"name": "publish_time", "type": "TIMESTAMP"},
            {"name": "demand_value", "type": "FLOAT"}
        ]
        df_empty = pd.DataFrame(columns=["timestamp", "publish_time", "demand_value"])
    else:
        schema = [
            {"name": "timestamp", "type": "TIMESTAMP"},
            {"name": "temperature_value", "type": "FLOAT"}
        ]
        df_empty = pd.DataFrame(columns=["timestamp", "temperature_value"])
    
    try:
        to_gbq(
            df_empty, 
            full_table_name, 
            project_id=PROJECT_ID,
            if_exists='replace', 
            table_schema=schema, 
            credentials=credentials
        )
        print(f"Successfully created table {full_table_name}")
    except Exception as e:
        print(f"Failed to create table {full_table_name}: {str(e)}")

# Pull temperature data from Elexon API
def pull_temperature_data(from_date, to_date):
    """Fetch temperature data from API"""
    url = f"https://data.elexon.co.uk/bmrs/api/v1/temperature?from={from_date}&to={to_date}&format=json"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if not data.get('data'):
            print("No temperature data in API response")
            return pd.DataFrame()
            
        processed = [{
            "timestamp": pd.to_datetime(x["measurementDate"]),
            "temperature_value": float(x["temperature"])
        } for x in data['data']]
        
        return pd.DataFrame(processed)
        
    except Exception as e:
        print(f"Error fetching temperature data: {str(e)}")
        return pd.DataFrame()

# Pull demand data from Elexon API
def pull_demand_data(from_date, to_date):
    url = f"https://data.elexon.co.uk/bmrs/api/v1/demand/outturn/daily?settlementDateFrom={from_date}&settlementDateTo={to_date}&format=json"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        if not data.get('data'):
            print("No demand data in API response")
            return pd.DataFrame()

        processed = [{
            "timestamp": pd.to_datetime(x["settlementDate"]),
            "publish_time": pd.to_datetime(x["publishTime"]),
            "demand_value": float(x["demand"])
        } for x in data['data']]

        return pd.DataFrame(processed)

    except Exception as e:
        print(f"Error fetching demand data: {str(e)}")
        return pd.DataFrame()

    
# Pull weather data from Visual Crossing API

def pull_weather_data(from_date, to_date):
    API_KEY = "YSMAWYWAAQUCN4STA4XFW68XA"
    BASE_URL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/United%20Kingdom"
    current = pd.to_datetime(from_date)
    end = pd.to_datetime(to_date)
    all_data = []

    while current <= end:
        month_start = current.strftime('%Y-%m-%d')
        month_end = (current + pd.offsets.MonthEnd(0)).strftime('%Y-%m-%d')
        url = f"{BASE_URL}/{month_start}/{month_end}?unitGroup=metric&include=days&key={API_KEY}&contentType=json"

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            json_data = response.json()
            if "days" not in json_data:
                print(f"No daily data found for {month_start} to {month_end}")
                current += pd.offsets.MonthBegin(1)
                continue

            days_data = json_data["days"]
            processed = [{
                "date": x["datetime"],
                "temp": x.get("temp"),
                "humidity": x.get("humidity"),
                "precip": x.get("precip"),
                "windspeed": x.get("windspeed"),
                "cloudcover": x.get("cloudcover")
            } for x in days_data]

            all_data.extend(processed)

        except Exception as e:
            print(f"Error fetching weather data for {month_start} to {month_end}: {str(e)}")

        current += pd.offsets.MonthBegin(1)

    return pd.DataFrame(all_data)



def load_incremental_data(credentials):
    if not check_table_exists(TABLE_TEMPERATURE, credentials):
        create_table(FULL_TABLE_TEMPERATURE, credentials)
    if not check_table_exists(TABLE_DEMAND, credentials):
        create_table(FULL_TABLE_DEMAND, credentials, is_demand=True)
    if not check_table_exists(WEATHER_TABLE, credentials):
        create_table(FULL_TABLE_WEATHER, credentials, is_weather=True)

    try:
        temp_latest_df = read_gbq(f"SELECT MAX(timestamp) as max_ts FROM `{FULL_TABLE_TEMPERATURE}`", project_id=PROJECT_ID, credentials=credentials)
        temp_latest = temp_latest_df.iloc[0, 0] if not temp_latest_df.empty and not pd.isna(temp_latest_df.iloc[0, 0]) else datetime(2024, 1, 1)
        new_temp = pull_temperature_data(temp_latest.strftime('%Y-%m-%d'), datetime.now().strftime('%Y-%m-%d'))
        if not new_temp.empty:
            existing_ts = read_gbq(f"SELECT DISTINCT timestamp FROM `{FULL_TABLE_TEMPERATURE}`", project_id=PROJECT_ID, credentials=credentials)['timestamp'].dt.normalize()
            new_temp['timestamp'] = pd.to_datetime(new_temp['timestamp']).dt.normalize()
            new_temp = new_temp[~new_temp['timestamp'].isin(existing_ts)]
            if not new_temp.empty:
                to_gbq(new_temp, FULL_TABLE_TEMPERATURE, project_id=PROJECT_ID, if_exists='append', credentials=credentials)
                print(f"Loaded {len(new_temp)} temperature records")
            else:
                print("No new temperature data to load")
    except Exception as e:
        print(f"Failed to process temperature data: {str(e)}")

    try:
        demand_latest_df = read_gbq(f"SELECT MAX(timestamp) as max_ts FROM `{FULL_TABLE_DEMAND}`", project_id=PROJECT_ID, credentials=credentials)
        demand_latest = demand_latest_df.iloc[0, 0] if not demand_latest_df.empty and not pd.isna(demand_latest_df.iloc[0, 0]) else datetime(2024, 1, 1)
        new_demand = pull_demand_data(demand_latest.strftime('%Y-%m-%d'), datetime.now().strftime('%Y-%m-%d'))
        if not new_demand.empty:
            existing_ts = read_gbq(f"SELECT DISTINCT timestamp FROM `{FULL_TABLE_DEMAND}`", project_id=PROJECT_ID, credentials=credentials)['timestamp'].dt.normalize()
            new_demand['timestamp'] = pd.to_datetime(new_demand['timestamp']).dt.normalize()
            new_demand = new_demand[~new_demand['timestamp'].isin(existing_ts)]
            if not new_demand.empty:
                to_gbq(new_demand[['timestamp', 'publish_time', 'demand_value']], FULL_TABLE_DEMAND, project_id=PROJECT_ID, if_exists='append', credentials=credentials)
                print(f"Loaded {len(new_demand)} demand records")
            else:
                print("No new demand records after deduplication.")
    except Exception as e:
        print(f"Failed to process demand data: {str(e)}")

    try:
        weather_latest_df = read_gbq(
            f"SELECT MAX(date) as max_date FROM `{FULL_TABLE_WEATHER}`",
            project_id=PROJECT_ID,
            credentials=credentials
        )
        weather_latest = (
            weather_latest_df.iloc[0, 0]
            if not weather_latest_df.empty and not pd.isna(weather_latest_df.iloc[0, 0])
            else datetime(2024, 1, 1)
        )

        new_weather = pull_weather_data(
            weather_latest.strftime('%Y-%m-%d'),
            datetime.now().strftime('%Y-%m-%d')
        )

        if not new_weather.empty:
            existing_dates = read_gbq(
                f"SELECT DISTINCT date FROM `{FULL_TABLE_WEATHER}`",
                project_id=PROJECT_ID,
                credentials=credentials
            )["date"].apply(lambda d: pd.to_datetime(d).date())

            new_weather["date"] = pd.to_datetime(new_weather["date"]).dt.date
            new_weather = new_weather[~new_weather["date"].isin(existing_dates)]

            if not new_weather.empty:
                to_gbq(
                    new_weather,
                    FULL_TABLE_WEATHER,
                    project_id=PROJECT_ID,
                    if_exists='append',
                    credentials=credentials
                )
                print(f"Loaded {len(new_weather)} weather records")
            else:
                print("No new weather data to load")
    except Exception as e:
        print(f"Failed to process weather data: {str(e)}")


# === Load data from BigQuery ===
def load_data(credentials):
    project_id = "sipa-adv-c-arshiya-ijaz"
    dataset = "elexon_energy"

    # Load weather data
    weather = read_gbq(
        f"SELECT date, temp, humidity, precip, windspeed, cloudcover FROM `{project_id}.{dataset}.weather`",
        project_id=project_id, credentials=credentials
    )
    weather["date"] = pd.to_datetime(weather["date"]).dt.date

    # Load demand data
    demand = read_gbq(
        f"SELECT timestamp, demand_value FROM `{project_id}.{dataset}.demand`",
        project_id=project_id, credentials=credentials
    )
    demand["date"] = pd.to_datetime(demand["timestamp"]).dt.date
    demand = demand.groupby("date", as_index=False).mean(numeric_only=True)

    # Load temperature data (note: `data` column holds temperature)
    temperature = read_gbq(
        f"SELECT timestamp, data FROM `{project_id}.{dataset}.temperature`",
        project_id=project_id, credentials=credentials
    )
    temperature["date"] = pd.to_datetime(temperature["timestamp"]).dt.date
    temperature = temperature.rename(columns={"data": "temp_elexon"})
    temperature = temperature.groupby("date", as_index=False).mean(numeric_only=True)

    return weather, demand, temperature

def merge_data(weather, demand, temperature):
    merged = (
        weather.merge(temperature, on="date", how="inner")
               .merge(demand, on="date", how="inner")
    )
    return merged


if __name__ == "__main__":
    credentials = get_bq_credentials() 
    load_incremental_data(credentials)

    # === Load, merge, and upload merged dataset ===
    weather, demand, temperature = load_data(credentials)
    final_df = merge_data(weather, demand, temperature)

    # Upload to BigQuery
    merged_schema = [
        {"name": "date", "type": "DATE"},
        {"name": "temp", "type": "FLOAT"},
        {"name": "humidity", "type": "FLOAT"},
        {"name": "precip", "type": "FLOAT"},
        {"name": "windspeed", "type": "FLOAT"},
        {"name": "cloudcover", "type": "FLOAT"},
        {"name": "temp_elexon", "type": "FLOAT"},
        {"name": "demand_value", "type": "FLOAT"}
    ]

    try:
        to_gbq(
            final_df,
            FULL_TABLE_MERGED,
            project_id=PROJECT_ID,
            if_exists='replace',
            table_schema=merged_schema,
            credentials=credentials
        )
        print(f"✅ Uploaded merged dataset to BigQuery table `{FULL_TABLE_MERGED}`")
    except Exception as e:
        print(f"❌ Failed to upload merged data: {str(e)}")

    # Save locally
    final_df.to_csv("merged_demand_weather_temp.csv", index=False)
    print("✅ Merged data saved to 'merged_demand_weather_temp.csv'")
    print(final_df.head())