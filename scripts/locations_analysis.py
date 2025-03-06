import pandas as pd
from temp_and_rainfall import get_location_info

df_ours = pd.read_excel("results/temp_and_rainfall.xlsx")
df_big = pd.read_excel("data/Reference_Froggy_Spreadsheet.xlsx")

missing_data_locs = []
loc_diffs = {}

for i, row in df_ours.iterrows():

    if i > 500:
        break

    genus, species = row["Name"].split(' ')

    print("Processing {}: {} {}".format(i, genus, species))
    
    locations = get_location_info(genus, species)
    
    if locations:

        ### WHICH LOCATIONS' RAINFALL ROWS ARE MISSING? ###

        if row["Min Rainfall"] == "-": # if one's missing, they all are
            for loc in locations:
                if loc not in missing_data_locs:
                    missing_data_locs.append(loc)
            continue

        ### WHICH LOCATIONS' RAINFALL ROWS ARE VERY INACCURATE? ###

        # get big reference spreadsheet's "Mean Temperature" value
        big_mean_temp = df_big.loc[df_big["Name"] == row["Name"]]["Mean Temperature"].values[0]
        our_mean_temp = row["Mean Temperature"]

        if not big_mean_temp or not our_mean_temp: # if either is missing, skip
            continue

        diff = abs(big_mean_temp - our_mean_temp)

        for loc in locations:
            if loc in loc_diffs:
                if diff > loc_diffs[loc]: # save the highest difference for each location
                    loc_diffs[loc] = diff
            else:
                loc_diffs[loc] = diff

sorted_diffs = sorted(loc_diffs.items(), key=lambda x: x[1], reverse=True)
print("Locations with highest discrepancies in mean rainfall: ")
print(sorted_diffs[:50])

print("Locations with missing rainfall data: ")
print(missing_data_locs)