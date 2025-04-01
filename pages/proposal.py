import streamlit as st

proposal_text = '''
**Proposal by**: Arshiya Sawhney (as5476) and Ijaz Ahmed Khan (ik2557)  

Streamlit app link: https://advanced-computing-elexon-energy-elexon-app-ie89eg.streamlit.app/temp_data_explore_part_4

**What dataset are you going to use?**  
We will be using the Elexon BSC’s IRIS Data Portal, which provides real-time, publicly-available data for the Great Britain electricity market.   
The 2 key datasets of interest from the platform are:   
1) Generation by Fuel Type: https://bmrs.elexon.co.uk/generation-by-fuel-type
    This dataset is updated every 5 minutes (also available at 30 min intervals)  
2) Daily average GB temperature: https://bmrs.elexon.co.uk/temperature
    This dataset is updated daily.

**What are your research question(s)?**  
1) What is the relationship between temperature and the source of energy generation? Trying to identify seasonality in generation data.  
2) We wish to create a forecasting model and test it with elexon's forecasts by training our model on historic data. We will try to use 
    the weather dataset and temperature as important features for our forecasting model. The aim is to find what features determine demand
    for energy.

**What's the link to your notebook?**    (we have moved everything to github)
    https://colab.research.google.com/drive/1T0LqML7dyQBx_vw7vp-7Ju5X5_FJ6Qaj?usp=sharing

**What's your target visualization?**  
    We will connect the temperature and energy generation datasets to explore the trend in temperature and total energy generation or renewable energy generation. The purpose is to explore seasonality, which might help identify which sources of energy should be most relied on based on weather conditions.
    We are also considering visualizing the differential between forecasted demand and actual generation on a daily basis to assess the accuracy of the forecasting model, which could look as follows, with date on the x-axis and (forecast-generation) on the y axis.

**What are your known unknowns?**  
    Our visualizations may not provide strong enough evidence to reach a conclusion on our hypothesis
    Energy generation is affected by many factors other than temperature, such as the installed capacity of power plans, which we do not have visibility on in the dataset 
    Datasets have been made publicly available and been published everyday without any miss till now, which ensures data availability

**What challenges do you anticipate?**  
    While it is a relatively clean dataset, we may run into issues interpreting and understanding technical terms related to the energy sector which we are not familiar with (such as outturn generation)
    Handling a large dataset (which is updated every 30 min or so) might be a challenge as it may require heavy processing power and very frequent changes may make our analysis confusing 
    Upcoming policy changes in UK’s energy sector or extreme events could affect/ disrupt the pattern of energy generation

    As we plan to create a forecasting model, identifying relevant features for e.g., weather data, holidays, or special events) and transforming raw data into meaningful inputs can be complex and time-consuming.
    There are various machine learning models to choose from, such as linear regression, decision trees, random forests. Each comes with its own advantages and limitations.
    and selecting the most suitable one requires experimentation.

** New Insights **   
    We observed an interesting relationship between temperature and demand for electricity and also the trend for electricity demand. Our visuals show that when temperature is low the demand for electricity 
    is higher which means that during the winter the demand for electricity is high but on the other hand, demand for electricity is lower when its summer. We plan to explore whether the source of electricity changes 
    significantly between these two seasons. It would be valuable to analyze which energy sources are more heavily utilized in winter versus summer. Additionally, given the availability of extensive historical data, 
    this could provide a strong foundation for developing a forecasting model for electricity demand in the UK. We also plan to compare our model's forecasts with those provided by Elexon on its website.

'''

st.markdown(proposal_text)

