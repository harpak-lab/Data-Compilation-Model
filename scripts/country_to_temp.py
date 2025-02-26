import pandas as pd
import requests

def find_location(name, file_path="data/geonames.xlsx"):
    xls = pd.ExcelFile(file_path) # get geonames excel

    countries_df = pd.read_excel(xls, sheet_name="Countries")
    country_match = countries_df[countries_df["Name"].str.lower() == name.lower()] # if name in countries sheet
    if not country_match.empty:
        return country_match.iloc[0]["ISO3 Code"] # ret country code
    
    subnationals_df = pd.read_excel(xls, sheet_name="Subnationals")
    subnational_match = subnationals_df[subnationals_df["Subnational Name"].str.lower() == name.lower()] # if name in subnationals sheet
    if not subnational_match.empty:
        return subnational_match.iloc[0]["Subnational Code"] # ret subnationals code
    
    print("Name not found.")
    
    return None

def get_data(code):
    url = f"https://cckpapi.worldbank.org/cckp/v1/cmip6-x0.25_climatology_tas_climatology_annual_1995-2014_median_historical_ensemble_all_mean/{code}?_format=json"
    response = requests.get(url) # get data from url
    
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("Failed to retrieve data. Status code:", response.status_code)
        return None

if __name__ == "__main__":
    name = "Sinaloa"
    code = find_location(name)
    if not code:
        exit()
    data = get_data(code)
    temp = float(list(data["data"][code].values())[-1]) # get the last value in KV (most recent year as far as I understand)
    print(temp)