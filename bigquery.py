import pandas as pd
import requests
import pydata_google_auth
from datetime import datetime
from google.oauth2 import service_account
import streamlit as st
from pathlib import Path

PROJECT_ID = "sipa-adv-c-arshiya-ijaz"
DATASET = "elexon_energy"
TABLE = "generation_data"
FULL_TABLE = f"{PROJECT_ID}.{DATASET}.{TABLE}"
SCOPES = [
    'https://www.googleapis.com/auth/cloud-platform',
    'https://www.googleapis.com/auth/drive']


def project_credentials():
    try:
        return service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])
    except Exception:
        credentials = pydata_google_auth.get_user_credentials(
        SCOPES,
        auth_local_webserver=True)
        return credentials

def get_latest_timestamp():
    query = f"""
    SELECT MAX(StartTime) as latest_timestamp
    FROM {FULL_TABLE}
    """
    try:
        credentials = project_credentials()
        df = read_gbq(query, project_id=PROJECT_ID, credentials=credentials)
        latest_timestamp = df['latest_timestamp'].iloc[0]
        if pd.isna(latest_timestamp):
            return datetime(datetime.now().year, 1, 1).strftime('%Y-%m-%d')
        if isinstance(latest_timestamp, str):
            latest_timestamp = datetime.strptime(latest_timestamp.split('T')[0], '%Y-%m-%d')
        return latest_timestamp.strftime('%Y-%m-%d')
    except Exception as e:
        st.write(e)
        return datetime(datetime.now().year, 1, 1).strftime('%Y-%m-%d')

def get_generation_data(from_date, to_date):
    api_url = f"https://data.elexon.co.uk/bmrs/api/v1/generation/actual/per-type?from={from_date}&to={to_date}&settlementPeriodFrom=1&settlementPeriodTo=48&format=json"
    api_response = requests.get(api_url)
    api_response = api_response.json()
    generation_data = api_response['data']
    return generation_data

def flatten_generation_data(original):
    result = {
        'StartTime': original['startTime'],
        'SettlementPeriod': original['settlementPeriod'],
    }
    for element in original['data']:
        psr_type = element['psrType']
        result[psr_type] = element['quantity']
    return result

def process_data(generation_data):
    df = pd.DataFrame(map(flatten_generation_data, generation_data))
    return df

def upload_to_gbq(df):
    try:
        credentials = project_credentials()
        to_gbq(df, destination_table=FULL_TABLE, project_id=PROJECT_ID, credentials=credentials, if_exists='append')
        print("Data uploaded to BigQuery")
    except Exception as e:
        print(f"Upload failed: {e}")


def main():
    latest_date_str = get_latest_timestamp()
    current_date_str = datetime.now().strftime('%Y-%m-%d')
    
    # Convert both to datetime objects to compare
    latest_date = datetime.strptime(latest_date_str, '%Y-%m-%d')
    current_date = datetime.strptime(current_date_str, '%Y-%m-%d')
    
    if latest_date < current_date:
        raw_data = get_generation_data(latest_date_str, current_date_str)
        if raw_data:
            df = process_data(raw_data)
            upload_to_gbq(df)

if __name__ == "__main__":
    main()