import requests
import streamlit as st
import pandas as pd
#import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
#from pages import temperature_data
#from temperature_data import fetch_temperature_data, flatten_tempdata



def fetch_temperature_data(api_url):
    response = requests.get(api_url)
    data = response.json()
    return data['data']

def flatten_tempdata(original):
  result = []
  for element in original:
    new_elemt = {}
    new_elemt['Date'] = element['measurementDate']
    new_elemt['Temperature'] = element['temperature']
    result.append(new_elemt)
  return result

temp_api = "https://data.elexon.co.uk/bmrs/api/v1/temperature?from=2024-01-01&to=2024-12-31&format=json"
temp_data = fetch_temperature_data(temp_api)
flattened_data = flatten_tempdata(temp_data)

df2 = pd.DataFrame(flattened_data)

def flatten_demand(original):
  result = []
  for element in original:
    new_elemt = {}
    new_elemt['Date'] = element['settlementDate']
    new_elemt['Demand'] = element['initialTransmissionSystemDemandOutturn']
    result.append(new_elemt)
  return result

demand_api= "https://data.elexon.co.uk/bmrs/api/v1/demand/peak?from=2024-01-01&to=2024-12-31&format=json"
demand_data = requests.get(demand_api)
demand_data = demand_data.json()
demand_data = demand_data['data']

daily_demand=flatten_demand(demand_data)
demand_df = pd.DataFrame(daily_demand)


df2['Date'] = pd.to_datetime(df2['Date']).dt.date
demand_df['Date'] = pd.to_datetime(demand_df['Date']).dt.date

# Now, merge again
merged_data = pd.merge(df2, demand_df, on='Date')



print(df2.head())
print(demand_df.head())
print(merged_data.head())



## PLOT
st.title("Temperature and Demand Over Time")

fig, ax1 = plt.subplots(figsize=(12, 6))

# Primary y-axis (Temperature)
ax1.set_xlabel('Date')
ax1.set_ylabel('Temperature (°C)', color='blue')
ax1.plot(merged_data['Date'], merged_data['Temperature'], label='Temperature', color='blue')
ax1.tick_params(axis='y', labelcolor='blue')

# Secondary y-axis (Demand)
ax2 = ax1.twinx()
ax2.set_ylabel('Demand (MW)', color='orange')
ax2.plot(merged_data['Date'], merged_data['Demand'], label='Demand', color='orange')
ax2.tick_params(axis='y', labelcolor='orange')

# Title and Grid
plt.title('Temperature and Demand Over Time')
fig.tight_layout()

# Show the plot outside of Streamlit
#plt.show()

# Show the plot in Streamlit
st.pyplot(fig)




## weather data

# weather_api"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/united%20kingdom/2024-01-01/2024-12-31?unitGroup=us&key=YSMAWYWAAQUCN4STA4XFW68XA&contentType=json"
# weather_data = temperature_data.fetch_temperature_data(weather_api)
