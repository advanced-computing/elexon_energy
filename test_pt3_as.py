import pandas as pd
import pytest
import json
from datetime import datetime 
from elexon_app import flatten_generationdata



def setup_test_data():
   with open("test_generation_data.json") as f:
    sample_data = json.load(f)
    sample_data = sample_data["data"]
    return sample_data

sample_data = setup_test_data()

#sample_row = {
        #"startTime": "2024.01.01",
       # "settlementPeriod": 1,
        #"data": [{"psrType": "Solar", "quantity": 100}]
#}

def test_flatten_generationdata_datetime_format():
    sample_output = list(map(flatten_generationdata, sample_data))
    sample_row = sample_output[0]
    try:
        datetime.strptime(sample_row["StartTime"], "%Y-%m-%dT%H:%M:%SZ")
        assert True 
    except AssertionError:
        print("The StartTime is not in a correct format")
    

def test_flatten_generationdata_fuel_type():
    sample_output = list(map(flatten_generationdata, sample_data))
    fuel_types = ["Biomass","Fossil Gas","Fossil Hard coal","Fossil Oil","Hydro Pumped Storage","Hydro Run-of-river and poundage","Nuclear","Other","Solar","Wind Offshore","Wind Onshore" ]
    for dict in sample_output:
       for key in dict.keys():
          if key not in ["StartTime", "SettlementPeriod"]:
            if key not in fuel_types:
               assert False
            

def test_flatten_generationdata_quantity_is_numeric():
    sample_output = list(map(flatten_generationdata, sample_data))
    for dict in sample_output:
        for key, value in dict.items():
            if key not in ["StartTime", "SettlementPeriod"]:
                value = float(value)
                if type(value)!=float:
                    assert False