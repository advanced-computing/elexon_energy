import pandas as pd
from pandas_gbq import to_gbq, read_gbq
import requests
import pydata_google_auth
#from google.oauth2 import service_account
from datetime import datetime

# configuration
PROJECT_ID = "sipa-adv-c-arshiya-ijaz"
DATASET = "elexon_energy"
TABLE_TEMPERATURE = "temperature"
TABLE_DEMAND = "demand"
FULL_TABLE_TEMPERATURE = f"{PROJECT_ID}.{DATASET}.{TABLE_TEMPERATURE}"
FULL_TABLE_DEMAND = f"{PROJECT_ID}.{DATASET}.{TABLE_DEMAND}"
SCOPES = [
    'https://www.googleapis.com/auth/cloud-platform',
    'https://www.googleapis.com/auth/drive'
]

PROJECT_ID = "sipa-adv-c-arshiya-ijaz"
DATASET = "elexon_energy"
TABLE_TEMPERATURE = "temperature"
TABLE_DEMAND = "demand"
FULL_TABLE_TEMPERATURE = f"{PROJECT_ID}.{DATASET}.{TABLE_TEMPERATURE}"
FULL_TABLE_DEMAND = f"{PROJECT_ID}.{DATASET}.{TABLE_DEMAND}"
SCOPES = ['https://www.googleapis.com/auth/cloud-platform',
          'https://www.googleapis.com/auth/drive'
]



# Authenticate with user credentials
credentials = pydata_google_auth.get_user_credentials(
    SCOPES,
    auth_local_webserver=True, 
    credentials_cache=pydata_google_auth.cache.REAUTH
)

def check_table_exists(table_name, credentials):
    """Check if a table exists in BigQuery"""
    query = f"""
    SELECT table_name 
    FROM `{PROJECT_ID}.{DATASET}.INFORMATION_SCHEMA.TABLES`
    WHERE table_name = '{table_name}'
    """
    try:
        df = read_gbq(
            query, 
            project_id=PROJECT_ID,
            credentials=credentials
        )
        return not df.empty
    except Exception as e:
        print(f"Error checking table existence: {str(e)}")
        return False

def create_table(full_table_name, credentials, is_demand=False):
    """Create a new table with appropriate schema"""
    if is_demand:
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

def pull_demand_data(from_date, to_date):
    """Fetch demand data from API"""
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
    
## Had to use chatgpt to find this code as I am completely new to this way of loading data
def load_incremental_data(credentials):
    """Main function to load both temperature and demand data"""
    # Initialize tables if they don't exist
    if not check_table_exists(TABLE_TEMPERATURE, credentials):
        print("Creating temperature table")
        create_table(FULL_TABLE_TEMPERATURE, credentials)
    
    if not check_table_exists(TABLE_DEMAND, credentials):
        print("Creating demand table")
        create_table(FULL_TABLE_DEMAND, credentials, is_demand=True)
    
    # Process temperature data
    try:
        temp_latest_df = read_gbq(
            f"SELECT MAX(timestamp) as max_ts FROM `{FULL_TABLE_TEMPERATURE}`",
            project_id=PROJECT_ID,
            credentials=credentials
        )
        
        # Handle case when table is empty
        temp_latest = temp_latest_df.iloc[0,0] if not temp_latest_df.empty and not pd.isna(temp_latest_df.iloc[0,0]) else datetime(2024, 1, 1)
        
        new_temp = pull_temperature_data(
            temp_latest.strftime('%Y-%m-%d') if not pd.isna(temp_latest) else '2024-01-01',
            datetime.now().strftime('%Y-%m-%d')
        )
        
        if not new_temp.empty:
            # Ensure column names match existing table schema
            new_temp = new_temp.rename(columns={"temperature_value": "data"})
            to_gbq(
                new_temp,
                FULL_TABLE_TEMPERATURE,
                project_id=PROJECT_ID,
                if_exists='append',
                credentials=credentials
            )
            print(f"Loaded {len(new_temp)} temperature records")
        else:
            print("No new temperature data to load")
    except Exception as e:
        print(f"Failed to process temperature data: {str(e)}")
    
    # Process demand data
    try:
        # First check if we need to migrate the schema
        if check_table_exists(TABLE_DEMAND, credentials):
            current_columns = read_gbq(
                f"SELECT column_name FROM `{PROJECT_ID}.{DATASET}.INFORMATION_SCHEMA.COLUMNS` "
                f"WHERE table_name = '{TABLE_DEMAND}'",
                project_id=PROJECT_ID,
                credentials=credentials
            )['column_name'].tolist()
            
            if 'publish_time' not in current_columns:
                print("Migrating demand table schema...")
                # Create temp table with new schema
                temp_table = f"{TABLE_DEMAND}_temp_{datetime.now().strftime('%Y%m%d')}"
                create_table(f"{PROJECT_ID}.{DATASET}.{temp_table}", credentials, is_demand=True)
                
                # Migrate data
                migrate_query = f"""
                INSERT INTO `{PROJECT_ID}.{DATASET}.{temp_table}` (timestamp, demand_value)
                SELECT timestamp, data as demand_value 
                FROM `{FULL_TABLE_DEMAND}`
                """
                read_gbq(migrate_query, project_id=PROJECT_ID, credentials=credentials)
                
                # Replace tables
                read_gbq(f"DROP TABLE `{FULL_TABLE_DEMAND}`", 
                        project_id=PROJECT_ID, 
                        credentials=credentials)
                read_gbq(f"ALTER TABLE `{PROJECT_ID}.{DATASET}.{temp_table}` "
                        f"RENAME TO `{TABLE_DEMAND}`", 
                        project_id=PROJECT_ID, 
                        credentials=credentials)
                print("Schema migration completed")

        # Now process demand data with proper schema
        demand_latest_df = read_gbq(
            f"SELECT MAX(timestamp) as max_ts FROM `{FULL_TABLE_DEMAND}`",
            project_id=PROJECT_ID,
            credentials=credentials
        )
        
        demand_latest = demand_latest_df.iloc[0,0] if not demand_latest_df.empty and not pd.isna(demand_latest_df.iloc[0,0]) else datetime(2024, 1, 1)
        
        new_demand = pull_demand_data(
            demand_latest.strftime('%Y-%m-%d') if not pd.isna(demand_latest) else '2024-01-01',
            datetime.now().strftime('%Y-%m-%d')
        )
        
        if not new_demand.empty:
            # Ensure column names match the current schema
            to_gbq(
                new_demand[['timestamp', 'publish_time', 'demand_value']],
                FULL_TABLE_DEMAND,
                project_id=PROJECT_ID,
                if_exists='append',
                credentials=credentials
            )
            print(f"Loaded {len(new_demand)} demand records")
        else:
            print("No new demand data to load")
            
    except Exception as e:
        print(f"Failed to process demand data: {str(e)}")

if __name__ == "__main__":
    load_incremental_data(credentials)