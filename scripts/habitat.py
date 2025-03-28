'''
From IUCN: Preferred Habitat (IUCN Habitat Categories) and one preferred habitat if available
'''

import os
import pandas as pd
from temp_and_rainfall import get_assessment_id, get_species_assessment

def habitat_codes(json_data):
    if "habitats" not in json_data:
        return []

    codes = set()
    for habitat in json_data["habitats"]:
        code = habitat.get("code")
        if code and isinstance(code, str) and "_" in code:
            top_level = code.split("_")[0]
            codes.add(top_level)

    return list(codes)

df = pd.read_excel("results/froggy_analysis_results.xlsx")

for i in range(1, 17):
    df[str(i)] = 0

for index, row in df.iterrows():

    name_parts = row["Name"].strip().split()
    if len(name_parts) < 2:
        continue

    print("Processing {}: {}".format(index, row["Name"]))

    genus, species = name_parts[0], name_parts[1]

    codes = []

    assessment_id = get_assessment_id(genus, species)

    if assessment_id:
        assessment_info = get_species_assessment(assessment_id)

        if assessment_info:
            codes = habitat_codes(assessment_info)

    for code in codes:
        if code in df.columns:
            df.at[index, code] = 1

if os.path.exists("results/froggy_analysis_results.xlsx"):
    os.remove("results/froggy_analysis_results.xlsx")

df.to_excel("results/froggy_analysis_results.xlsx", index=False)