import os
from dotenv import load_dotenv
import requests
import pandas as pd

load_dotenv()

### PART 1: DERIVING LOCATIONS FROM SPECIES ###

TAXA_API_URL = "https://api.iucnredlist.org/api/v4/taxa/scientific_name"
ASSESSMENT_API_URL = "https://api.iucnredlist.org/api/v4/assessment"

API_KEY = os.getenv("IUCN_API_KEY")

def get_assessment_id(genus, species):
    url = f"{TAXA_API_URL}?genus_name={genus}&species_name={species}"
    headers = {
        "accept": "application/json",
        "Authorization": API_KEY
    }

    # get information for genus and species
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        assessments = data.get("assessments", []) # locate assessment id
        if assessments:
            latest_assessment = next((a for a in assessments if a["latest"]), None)
            if latest_assessment:
                return latest_assessment["assessment_id"]
        print(f"No assessments found for {genus} {species}.")
    else:
        print(f"Status code {response.status_code}")
    
    return None

def get_species_assessment(assessment_id):
    url = f"{ASSESSMENT_API_URL}/{assessment_id}"
    headers = {
        "accept": "application/json",
        "Authorization": API_KEY
    }

    # get species info from assessment id
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Status code {response.status_code}")
        return None

def get_location_info(genus, species):
    assessment_id = get_assessment_id(genus, species)

    if assessment_id:
        assessment_info = get_species_assessment(assessment_id)
        if assessment_info:
            if "locations" in assessment_info:
                # grab location data from species info
                locations = [loc["description"]["en"] for loc in assessment_info["locations"]]
                return locations
            else:
                print("No location data found.")
                return None
    else:
        print(f"Can't get assessment id.")
        return None

### PART 2: DERIVING TEMPERATURE AND RAINFALL FROM LOCATIONS ###

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
    url = f"https://cckpapi.worldbank.org/cckp/v1/cmip6-x0.25_climatology_tas,pr_climatology_annual_1995-2014_median_historical_ensemble_all_mean/{code}?_format=json"
    response = requests.get(url) # get data from url
    
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("Failed to retrieve data. Status code:", response.status_code)
        return None

def temp_and_rainfall(name):
    code = find_location(name)
    if not code:
        return None, None
    data = get_data(code)
    if not data:
        return None, None
    temp = float(list(data["data"]["tas"][code].values())[-1]) # get the last value in KV (most recent year as far as I understand)
    rainfall = float(list(data["data"]["pr"][code].values())[-1])
    return temp, rainfall

### PART 3: COMBINE PROCESSES TO GET INFO FOR ALL SPECIES ###

# read in initial results spreadsheet
results_spreadsheet = "results/egg_analysis_results.xlsx"
df_ref = pd.read_excel(results_spreadsheet)

# add columns for min, max, and mean temperature and rainfall
df_ref["Min Temperature"] = None
df_ref["Max Temperature"] = None
df_ref["Mean Temperature"] = None
df_ref["Min Rainfall"] = None
df_ref["Max Rainfall"] = None
df_ref["Mean Rainfall"] = None

for i, row in df_ref.iterrows():
    if i > 10:
        break

    all_temps = []
    all_rainfalls = []

    genus, species = row["Name"].split(' ')

    # process each location
    locations = get_location_info(genus, species)
    for location in locations:
        temp, rainfall = temp_and_rainfall(location)
        if temp is not None:
            all_temps.append(temp)
        if rainfall is not None:
            all_rainfalls.append(rainfall)
    
    # update temperature and rainfall values in spreadsheet
    if all_temps:
        df_ref.at[i, "Min Temperature"] = min(all_temps)
        df_ref.at[i, "Max Temperature"] = max(all_temps)
        df_ref.at[i, "Mean Temperature"] = sum(all_temps) / len(all_temps)
    else:
        df_ref.at[i, "Min Temperature"] = '-'
        df_ref.at[i, "Max Temperature"] = '-'
        df_ref.at[i, "Mean Temperature"] = '-'

    if all_rainfalls:
        df_ref.at[i, "Min Rainfall"] = min(all_rainfalls)
        df_ref.at[i, "Max Rainfall"] = max(all_rainfalls)
        df_ref.at[i, "Mean Rainfall"] = sum(all_rainfalls) / len(all_rainfalls)
    else:
        df_ref.at[i, "Min Rainfall"] = '-'
        df_ref.at[i, "Max Rainfall"] = '-'
        df_ref.at[i, "Mean Rainfall"] = '-'

# write to new spreadsheet
df_ref.to_excel("results/new_results.xlsx", index=False)