import os
from dotenv import load_dotenv
import requests
import pandas as pd
import time

load_dotenv()

# Constants for API endpoints
TAXA_API_URL = "https://api.iucnredlist.org/api/v4/taxa/scientific_name"
ASSESSMENT_API_URL = "https://api.iucnredlist.org/api/v4/assessment"
API_KEY = os.getenv("IUCN_API_KEY")

# Retrieve the latest IUCN assessment ID for a given species
def get_assessment_id(genus, species):
    url = f"{TAXA_API_URL}?genus_name={genus}&species_name={species}"
    headers = {
        "accept": "application/json",
        "Authorization": API_KEY
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        assessments = data.get("assessments", [])
        if assessments:
            latest_assessment = next((a for a in assessments if a["latest"]), None)
            if latest_assessment:
                return latest_assessment["assessment_id"]
        print(f"No assessments found for {genus} {species}.")
    else:
        print(f"Status code {response.status_code}")
    
    return None

# Retrieve full IUCN assessment JSON given an assessment ID
def get_species_assessment(assessment_id):
    url = f"{ASSESSMENT_API_URL}/{assessment_id}"
    headers = {
        "accept": "application/json",
        "Authorization": API_KEY
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Status code {response.status_code}")
        return None

# Match location names to CCKP-compatible region or country codes using geonames.xlsx
def find_location(locations, file_path="01_frog_data_compilation/data/geonames.xlsx"):
    xls = pd.ExcelFile(file_path)

    countries_df = pd.read_excel(xls, sheet_name="Countries")
    subnationals_df = pd.read_excel(xls, sheet_name="Subnationals")

    region_codes = []
    region_countries = []
    country_codes = []

    # First check subnational regions (e.g., states/provinces)
    for name in locations:
        subnational_match = subnationals_df[subnationals_df["Subnational Name"].str.lower() == name.lower()] # if name in subnationals sheet
        if not subnational_match.empty:
            region_codes.append(subnational_match.iloc[0]["Subnational Code"]) # subnationals code
            region_countries.append(subnational_match.iloc[0]["Country Code"])

    # Then check country-level matches (avoid duplicates)
    for name in locations:
        country_match = countries_df[countries_df["Name"].str.lower() == name.lower()] # if name in countries sheet
        if not country_match.empty:
            if not country_match.iloc[0]["ISO3 Code"] in region_countries:
                country_codes.append(country_match.iloc[0]["ISO3 Code"]) # country code
    
    return list(region_codes) + list(country_codes)

# Get temperature and rainfall data for a location code from the World Bank CCKP API
def get_data(code):
    url = f"https://cckpapi.worldbank.org/cckp/v1/cmip6-x0.25_climatology_tas,pr_climatology_annual_1995-2014_median_historical_ensemble_all_mean/{code}?_format=json"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data
    elif response.status_code == 429:
        print("Rate limit hit. Waiting before retrying...")
        time.sleep(10)
        return get_data(code)
    else:
        print("Failed to retrieve data. Status code:", response.status_code)
        return None