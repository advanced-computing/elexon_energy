import streamlit as st
import pandas as pd
import requests
import plotly.express as px

api_url1 = "https://data.elexon.co.uk/bmrs/api/v1/generation/actual/per-type?from=2024-01-01&to=2024-01-03&settlementPeriodFrom=1&settlementPeriodTo=48&format=json"

generation_by_fuel = requests.get(api_url1)
generation_json = generation_by_fuel.json()
generation_data = generation_json['data']

def flatten_generationdata(original):
  result = {
      'StartTime': original['startTime'],
      'SettlementPeriod':original['settlementPeriod'],
  }

  for element in original['data']:
    psr_type = element['psrType']
    result[psr_type] = element['quantity']

  return result


df1 = list(map(flatten_generationdata, generation_data))

df1 = pd.DataFrame(df1)

st.markdown("# Home Page")
st.sidebar.markdown("# Home Page")

st.title("Elexon Energy - UK Electricity Data")
st.write("Project Team: Arshiya Sawhney and Ijaz Ahmed Khan")
st.write("Data Summary/ Structure:")
st.dataframe(df1.head())

total_by_source = df1.iloc[:, 1:].sum()
total_row = pd.DataFrame([["Total"] + total_by_source.tolist()], columns=df1.columns)
df1 = pd.concat([df1, total_row], ignore_index=True)

totals = df1.iloc[:, 1:].sum().reset_index()
totals.columns = ["Fuel Source", "Total Generation"]

fuel_types = ["Biomass","Fossil Gas","Fossil Hard coal","Fossil Oil","Hydro Pumped Storage","Hydro Run-of-river and poundage","Nuclear","Other","Solar","Wind Offshore","Wind Onshore" ]

fig1 = px.histogram(totals, x="Fuel Source", y="Total Generation", title="Total Generation by Fuel Type (01/01/2024 - 01/03/2024)")
st.plotly_chart(fig1)


