import streamlit as st
import datetime
import bigquery
from functions.data_processing import load_data, calculate_totals
from functions.visualization import plot_generation_bar_chart, plot_generation_pie_chart, plot_generation_sparkline
from functions.metrics import display_top_fuel_metrics


def main():
    st.title("Elexon Energy - UK Electricity Data")
    st.write("Project Team: Arshiya Sawhney and Ijaz Ahmed Khan")
    
    # Show last update time in sidebar
    st.sidebar.header("Data Updates")
    last_update = bigquery.get_latest_timestamp()  # This returns a string in YYYY-MM-DD format
    # Convert string to datetime for better display
    last_update_dt = datetime.datetime.strptime(last_update, '%Y-%m-%d')
    st.sidebar.write(f"Last data update: {last_update_dt.strftime('%d/%m/%Y')}")
    
    st.sidebar.header("Select Dates")
    
    # Set default dates based on available data
    min_allowed_date = datetime.date(2024, 1, 1)
    default_start_date = min_allowed_date
    default_end_date = datetime.date.today()
    
    start_date = st.sidebar.date_input("Start Date", default_start_date, min_value=min_allowed_date)
    end_date = st.sidebar.date_input("End Date", default_end_date, min_value=min_allowed_date)
    
    if start_date > end_date:
        st.error("Error: End date must be after start date.")
        return
    
    df = load_data(start_date, end_date)
    df, totals = calculate_totals(df)

    tab1, tab2, tab3 = st.tabs(["Leading Energy Sources", "Generation Split", "Trends Over Time"])
    
    with tab1:
        st.header("Leading Energy Sources")
        plot_generation_bar_chart(totals, start_date, end_date)
        display_top_fuel_metrics(totals)
    
    with tab2:
        st.header("Generation Split")
        plot_generation_pie_chart(totals, start_date, end_date)
    
    with tab3:
        st.header("Trends Over Time")
        trend_df = plot_generation_sparkline(df)
        st.dataframe(
            trend_df,
            column_config={
                "Fuel Source": st.column_config.TextColumn("Fuel Type"),
                "Generation Trend": st.column_config.LineChartColumn(
                    f"Generation by Settlement Period (MW) ({start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')})",
                    width="large",
                    help="Actual electricity generation at each settlement period (MW)"
                )
            },
            hide_index=True
        )

if __name__ == "__main__":
    main()