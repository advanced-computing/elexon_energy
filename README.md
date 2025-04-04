# Elexon Energy Data Analysis

We will be anlayzing energy generation data by fuel type for Great Britain. We aim to analyze seasonality by plotting generation by fuel type against daily average temperature. We may also compare daily forecast and actual generation to assess how accurate the forecasting model is.

### Streamlit app: 
https://advanced-computing-elexon-energy-elexon-app-ie89eg.streamlit.app/

### Data Loading rationale:
We believe 'Incremental' data loading is the ideal option for our project because it retrieves the new energy generation data from the API only. Since the generation dataset does not change for previous dates, there is no need to re-load them or keep an extra copy of the older generation datapoints. Therefore, using incremental load is appropriate in this case, will help avoid redundant data storage and processing and also improve efficiency for our project.

## Setup Instructions

1. Clone the "elexon_energy" repository from the advanced_computing github.
2. Create a virtual environment and install the dependencies by running the requirements .txt script (this should include Streamlit)
3. To access the app, run the following in a new terminal/ command line: "streamlit run elexon_app". This will lead you to the Home Page for the site. The app currently has 3 pages - 1) The main page with energy generation data; 2) The Proposal for the project; 3) Exploring Temperature and Energy Demand data (work in progress).