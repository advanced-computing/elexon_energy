import json
from datetime import datetime 
from utils.data_processing import flatten_generation_data



def setup_test_data():
   with open("test_generation_data.json") as f:
    sample_data = json.load(f)
    sample_data = sample_data["data"]
    return sample_data

sample_data = setup_test_data()

def test_flatten_generation_data_datetime_format():
    sample_output = list(map(flatten_generation_data, sample_data))
    sample_row = sample_output[0]
    try:
        datetime.strptime(sample_row["StartTime"], "%Y-%m-%dT%H:%M:%SZ")
        assert True 
    except AssertionError:
        print("The StartTime is not in a correct format")
    

def test_flatten_generation_data_fuel_type():
    sample_output = list(map(flatten_generation_data, sample_data))
    fuel_types = ["Biomass","Fossil Gas","Fossil Hard coal","Fossil Oil","Hydro Pumped Storage","Hydro Run-of-river and poundage","Nuclear","Other","Solar","Wind Offshore","Wind Onshore" ]
    for dict in sample_output:
       for key in dict.keys():
          if key not in ["StartTime", "SettlementPeriod"]:
            if key not in fuel_types:
               assert False
            

def test_flatten_generation_data_quantity_is_numeric():
    sample_output = list(map(flatten_generation_data, sample_data))
    for dict in sample_output:
        for key, value in dict.items():
            if key not in ["StartTime", "SettlementPeriod"]:
                try:
                    value = float(value)
                except AssertionError:
                   assert False