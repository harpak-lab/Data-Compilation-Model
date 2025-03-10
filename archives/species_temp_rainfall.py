import pandas as pd
from archives.species_to_country import get_location_info
from archives.country_to_temp import temp_and_rainfall

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