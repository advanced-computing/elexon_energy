# Elexon Energy Data Analysis

We will be anlayzing energy generation data by fuel type for Great Britain. We aim to analyze seasonality by plotting generation by fuel type against daily average temperature. We may also compare daily forecast and actual generation to assess how accurate the forecasting model is.

Streamlit app: https://advanced-computing-elexon-energy-elexon-app-ie89eg.streamlit.app/

## Data Loading: 
We believe 'Incremental' data loading is the ideal option for our project because it retrieves the new energy generation data from the API only. Since the generation dataset does not change for previous dates, there is no need to re-load them or keep an extra copy of the older generation datapoints. Therefore, using incremental load is appropriate in this case, will help avoid redundant data storage and processing and also improve efficiency for our project. 