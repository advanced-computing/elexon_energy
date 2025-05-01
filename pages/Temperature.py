import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Set the backend before other matplotlib calls
from pandas_gbq import read_gbq
from google.oauth2 import service_account
#from datetime import datetime
#from google.cloud import bigquery
import time
import plotly.graph_objects as go

# ML libraries
# import joblib
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import seaborn as sns


st.set_page_config(page_title="Temperature-Demand prediction", layout="wide")

# Configuration from secrets
PROJECT_ID = st.secrets["gcp_service_account"]["project_id"]
DATASET = "elexon_energy"
TEMPERATURE_TABLE = "temperature"
DEMAND_TABLE = "demand"
MERGED_TABLE = "merged_data"

# Authenticate
credentials_info = st.secrets["gcp_service_account"]
credentials = service_account.Credentials.from_service_account_info(
    credentials_info,
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)



# === Cache full dataset ===
@st.cache_data(show_spinner=True)
def load_full_merged_data():
    query = f"""
    SELECT *
    FROM `{PROJECT_ID}.{DATASET}.{MERGED_TABLE}`
    """
    df = read_gbq(query, project_id=PROJECT_ID, credentials=credentials)
    df['date'] = pd.to_datetime(df['date'])
    return df.sort_values("date")


# === Plot ===
def plot_temp_demand(data):
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Temperature (°C)', color='blue')
    ax1.plot(data['date'], data['temp_elexon'], color='blue', label='Temperature')
    ax1.tick_params(axis='y', labelcolor='blue')

    ax2 = ax1.twinx()
    ax2.set_ylabel('Demand (MW)', color='orange')
    ax2.plot(data['date'], data['demand_value'], color='orange', label='Demand')
    ax2.tick_params(axis='y', labelcolor='orange')

    plt.title('Temperature and Demand Over Time')
    fig.tight_layout()
    return fig

# Prediction model and plot function

def build_and_plot_prediction(df):
    st.subheader("🔮 Demand Prediction Over Time")

    # Prepare data
    df_model = df[['date', 'temp_elexon', 'humidity', 'cloudcover', 'windspeed', 'demand_value']].dropna()

    X = df_model[['temp_elexon', 'humidity', 'cloudcover', 'windspeed']]
    y = df_model['demand_value']
    dates = df_model['date']

    X_train, X_test, y_train, y_test, dates_train, dates_test = train_test_split(
        X, y, dates, test_size=0.3, random_state=42
    )

    # Train model
    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    # Performance metrics
    r2 = r2_score(y_test, y_pred)
    precision = 100 * (1 - mean_absolute_error(y_test, y_pred) / y_test.mean())

    st.write(f"**Model R² Score:** {r2:.2f}")
    st.write(f"**Prediction Precision:** {precision:.2f}%")

    # Create DataFrame for plotting
    plot_df = pd.DataFrame({
        'date': dates_test,
        'Actual Demand': y_test,
        'Predicted Demand': y_pred
    }).sort_values("date")

    # Plot
    fig = go.Figure()

    # Actual demand as dots
    fig.add_trace(go.Scatter(
        x=plot_df['date'], y=plot_df['Actual Demand'],
        mode='markers',
        name='Actual Demand',
        marker=dict(color='blue', size=6),
        hovertemplate='Date: %{x}<br>Actual: %{y:.0f} MW<extra></extra>'
    ))

    # Predicted demand as line
    fig.add_trace(go.Scatter(
        x=plot_df['date'], y=plot_df['Predicted Demand'],
        mode='lines',
        name='Predicted Demand',
        line=dict(color='red', width=2),
        hovertemplate='Date: %{x}<br>Predicted: %{y:.0f} MW<extra></extra>'
    ))

    fig.update_layout(
        title="Actual vs Predicted Demand Over Time",
        xaxis_title="Date",
        yaxis_title="Demand (MW)",
        hovermode="x unified",
        legend=dict(x=0, y=1.1, orientation='h'),
        margin=dict(l=30, r=30, t=50, b=30)
    )

    st.plotly_chart(fig, use_container_width=True)

# === Main ===
def main():
    page_start = time.time()

    st.title("📊 Demand, Temperature and Weather Analysis and Prediction")

    with st.spinner("Loading data..."):
        df = load_full_merged_data()
    st.success("Data loaded and cached!")

    # === Data Preview ===
    # Interactive row selector for viewing full dataset in chunks of 10
    st.write("### Explore merged dataset (10 rows at a time)")
    start_row = st.number_input("Start row", min_value=0, max_value=len(df)-1, step=10, value=0)
    st.dataframe(df.iloc[start_row:start_row+10], use_container_width=True)

    # === Date range selector ===
    st.markdown("#### Explore relationship between temperature and demand")
    st.markdown("We were interested to see the relationship between temperature and demand")
    st.markdown("""
        # Analysis  
        - **Seasonality**: Demand rises in colder months (negative correlation with temperature).
        """)

    min_date, max_date = df['date'].min(), df['date'].max()
    selected_range = st.date_input("Select date range", value=[min_date, max_date], min_value=min_date, max_value=max_date)

    if len(selected_range) == 2:
        start_date, end_date = selected_range
        filtered = df[(df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))]

        if not filtered.empty:
            fig = plot_temp_demand(filtered)
            st.pyplot(fig)
        else:
            st.warning("No data available for selected date range.")
    
    st.write("### Exploratory Data Analysis")

    # Compute correlation matrix
    corr = df.corr(numeric_only=True)

    # Show correlation matrix as table
    with st.expander("Show Correlation Matrix Table"):
        st.dataframe(corr, use_container_width=True)

    # Show heatmap
    with st.expander("Show Correlation Heatmap"):
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
        st.pyplot(fig)
    
    st.markdown("### Correlation Analysis")
    st.markdown(
        "We assess the linear relationships between weather-related variables "
        "(humidity, temperature, cloud cover) and demand for energy. "
        "The results highlight key drivers of demand, with **humidity** and **temperature** "
        "showing the strongest associations.",
        help="This analysis uses Pearson correlation on numerical variables."
    )
    with st.expander("🚀 Run Prediction Model"):
        build_and_plot_prediction(df)

    page_end = time.time()
    st.markdown(f"⏱ **Total page load time: {page_end - page_start:.2f} seconds**")

if __name__ == "__main__":
    main()

