# Elexon Energy Data Analysis

We will be anlayzing energy generation data by fuel type for Great Britain. We aim to analyze seasonality by plotting generation by fuel type against daily average temperature. We may also compare daily forecast and actual generation to assess how accurate the forecasting model is.

### Streamlit app: 
https://advanced-computing-elexon-energy-elexon-app-ie89eg.streamlit.app/

### Datasets
1. [Energy Generation](https://bmrs.elexon.co.uk/generation-by-fuel-type) 
2. [Energy Demand](https://bmrs.elexon.co.uk/demand-outturn) 
3. [Temperature](https://bmrs.elexon.co.uk/temperature) 
3. [Weather data](https://www.visualcrossing.com/weather-query-builder/) 

### Data Loading rationale:
We believe 'Incremental' data loading is the ideal option for our project because it retrieves the new energy generation data from the API only. Since the generation dataset does not change for previous dates, there is no need to re-load them or keep an extra copy of the older generation datapoints. Therefore, using incremental load is appropriate in this case, will help avoid redundant data storage and processing and also improve efficiency for our project.

## Setup Instructions

1. Clone the "[elexon_energy](https://github.com/advanced-computing/elexon_energy)" repository using the URL or git clone https://github.com/advanced-computing/elexon_energy.git.

2. Create a virtual environment to manage dependencies using  python -m venv .venv

3. Activate the environment by running the following command source .venv/bin/activate if you are a Mac user. If you are a Windows user then use .venv\Scripts\activate

4. Install the dependencies using the code <pre> ``` pip install -r requirements.txt ``` </pre> (NOTE: Make sure Streamlit in included in requirements.txt)

4. To access the app, run the following in a new terminal/ command line: "streamlit run elexon_app". 

This will open the app in your browser. The current version of the dashboard includes:

a. Main Page – Visualizes energy generation data.

b. Project Proposal – Outlines the goals and background of the project.

c. Temperature & Demand Analysis (Work in Progress) – Explores the relationship between temperature and energy demand.
