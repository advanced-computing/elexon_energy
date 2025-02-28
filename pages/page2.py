import requests
import streamlit as st
import pandas as pd
import plotly.express as px

# temp_api = "https://data.elexon.co.uk/bmrs/api/v1/temperature?from=2024-01-01&to=2024-01-03&format=json"
# temp_data = requests.get(temp_api)
# temp_data = temp_data.json()
# temp_data = temp_data['data']

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

temp_api = "https://data.elexon.co.uk/bmrs/api/v1/temperature?from=2024-01-01&to=2024-01-03&format=json"
temp_data = fetch_temperature_data(temp_api)
flattened_data = flatten_tempdata(temp_data)


df2 = list(flatten_tempdata(temp_data))
df2 = pd.DataFrame(df2)

st.markdown("# UK Temperature Data")
st.sidebar.markdown("# UK Temperature Data")
fig2 = px.line(df2, x="Date", y="Temperature", title="Daily Average Temperature")
st.plotly_chart(fig2)


#print(temp_data)
