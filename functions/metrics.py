import streamlit as st

@st.cache_data(ttl=3600)
def display_top_fuel_metrics(totals):
    """Streamlit metrics for the top 3 fuel types by generation"""
    sorted_totals = totals.sort_values("Total Generation", ascending=False)
    top_3_fuels = sorted_totals.head(3)
    
    st.write("### Top Fuel Sources (MW)")
    
    for _, row in top_3_fuels.iterrows():
        fuel_name = row["Fuel Source"]
        generation_value = row["Total Generation"]
        
        formatted_value = f"{generation_value / 1_000_000:.2f}M"
        
        st.metric(
            label=f"{fuel_name}",
            value=formatted_value) 