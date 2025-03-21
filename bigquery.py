import pandas as pd
from pandas_gbq import to_gbq
import requests
import pydata_google_auth

api_url = "https://data.elexon.co.uk/bmrs/api/v1/generation/actual/per-type?from=2024-01-01&to=2025-01-01&settlementPeriodFrom=1&settlementPeriodTo=48&format=json"

def get_generation_data(api_url):
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

PROJECT_ID = "sipa-adv-c-arshiya-ijaz"
DATASET = "elexon_energy"
TABLE = "generation_data"
FULL_TABLE = f"{PROJECT_ID}.{DATASET}.{TABLE}"

SCOPES = [
    'https://www.googleapis.com/auth/cloud-platform',
    'https://www.googleapis.com/auth/drive']

credentials = pydata_google_auth.get_user_credentials(
    SCOPES,
    auth_local_webserver=True,
)

def upload_to_gbq(df):
    try:
        to_gbq(df, destination_table=FULL_TABLE, project_id=PROJECT_ID, credentials=credentials, if_exists='append')
        print("Data uploaded to BigQuery")
    except Exception as e:
        print(f"Upload failed: {e}")


def main():
    raw_data = get_generation_data(api_url)
    df = process_data(raw_data)
    upload_to_gbq(df)

if __name__ == "__main__":
    main()