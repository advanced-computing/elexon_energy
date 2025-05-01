import pandas as pd
import pandas_gbq
import bigquery
import requests

def load_data(start_date, end_date):
    bigquery.main()
    credentials = bigquery.project_credentials()

    sql = f"""
        SELECT *
        FROM sipa-adv-c-arshiya-ijaz.elexon_energy.generation_data
        WHERE DATE(StartTime) >= '{start_date}'
        AND DATE(StartTime) <= '{end_date}'
        ORDER BY StartTime
    """
    return pandas_gbq.read_gbq(sql, bigquery.PROJECT_ID, credentials=credentials)

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
    """Calculates total electricity generation by fuel source for the time period the user selected"""
    total_by_source = df.iloc[:, 1:].sum()
    total_row = pd.DataFrame([['Total'] + total_by_source.tolist()], columns=df.columns)
    df = pd.concat([df, total_row], ignore_index=True)
    totals = df.iloc[:, 1:].sum().reset_index()
    totals.columns = ["Fuel Source", "Total Generation"]
    return df, totals 