import os
import pandas as pd
from dotenv import load_dotenv
from temp_and_rainfall import get_assessment_id, get_species_assessment

load_dotenv()

# read in spreadsheet to dataframe
results_spreadsheet = "results/froggy_analysis_results.xlsx"
df_ref = pd.read_excel(results_spreadsheet)

# new cols for altitude
df_ref["Min Altitude"] = None
df_ref["Max Altitude"] = None

for i, row in df_ref.iterrows():
    genus, species = row["Name"].split(' ')

    print(f"Processing {i}: {genus} {species}")

    # get info for species; same way as temp_and_rainfall
    assessment_id = get_assessment_id(genus, species)
    if assessment_id:
        species_info = get_species_assessment(assessment_id)
        if species_info:
            # get altitude info
            supplementary_info = species_info.get("supplementary_info", {})
            min_altitude = supplementary_info.get("lower_elevation_limit", None)
            max_altitude = supplementary_info.get("upper_elevation_limit", None)
        else:
            min_altitude, max_altitude = None, None
    else:
        min_altitude, max_altitude = None, None

    # save to dataframe
    df_ref.at[i, "Min Altitude"] = min_altitude if min_altitude is not None else "-"
    df_ref.at[i, "Max Altitude"] = max_altitude if max_altitude is not None else "-"

# remove existing spreadsheet and write new data to it
if os.path.exists("results/froggy_analysis_results.xlsx"):
    os.remove("results/froggy_analysis_results.xlsx")

df_ref.to_excel("results/froggy_analysis_results.xlsx", index=False)
print("Updated file saved to results/froggy_analysis_results.xlsx")