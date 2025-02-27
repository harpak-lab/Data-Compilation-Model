import requests
import os
from dotenv import load_dotenv

load_dotenv()

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