'''
https://amphibiaweb.org/api/ws.html
'''

import os
from bs4 import BeautifulSoup
import requests
from openai import AzureOpenAI
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

def get_url(genus, species):
    base_url = "https://amphibiaweb.org/cgi/amphib_ws"
    return f"{base_url}?where-genus={genus}&where-species={species}&src=amphibiaweb"

def get_xml(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        # check if page exists
        soup = BeautifulSoup(response.text, 'lxml-xml')
        error_tag = soup.find("error")
        if error_tag:
            return "NONEXISTENT PAGE"

        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def query_page(text):

    client = AzureOpenAI(
        api_key=os.getenv("AZURE_API_KEY"),
        api_version=os.getenv("AZURE_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_ENDPOINT")
    )

    prompts = {
        "male_svl": "Extract and return only the Male SVL (snout-vent length) from the following text, measured in **millimeters (mm)**. If a range is provided, return it in the format `avg` +- `uncertainty` (where the first value is the average and the second is half the range). If only a single value is present, return it in the format `avg` +- `0`. If not available, respond with '-'.\n\nText: {text}\n\nResponse:",
        "female_svl": "Extract and return only the Female SVL (snout-vent length) from the following text, measured in **millimeters (mm)**. If a range is provided, return it in the format `avg` +- `uncertainty` (where the first value is the average and the second is half the range). If only a single value is present, return it in the format `avg` +- `0`. If not available, respond with '-'.\n\nText: {text}\n\nResponse:",
        "avg_svl": "Extract and return only the **average SVL (snout-vent length)** from the following text, measured in **millimeters (mm)**. If separate values for males and females are provided, compute their **overall average** and return it in the format `avg` +- `uncertainty` (where `avg` is the mean of all values and `uncertainty` is half the range). If only a single value is present, return it in the format `avg` +- `0`. If not available, respond with '-'.\n\nText: {text}\n\nResponse:",
        "min_clutch_size": "Extract and return only the **minimum** egg clutch size from the following text. This refers to the **number of eggs laid per clutch**, given as a **whole number** or the **lower value of a range** (e.g., '50 eggs' from '50-200 eggs'). If only a single value is present, return that value. If not available, respond with '-'.\n\nText: {text}\n\nResponse:",
        "max_clutch_size": "Extract and return only the **maximum** egg clutch size from the following text. This refers to the **number of eggs laid per clutch**, given as a **whole number** or the **higher value of a range** (e.g., '200 eggs' from '50-200 eggs'). If only a single value is present, return that value. If not available, respond with '-'.\n\nText: {text}\n\nResponse:",
        "egg_diameter": "Extract and return only the average egg diameter from the following text, measured in **millimeters (mm)**. If a range is provided, return it in the format `avg` +- `uncertainty` (where the first value is the average and the second is half the range). If only a single value is present, return it in the format `avg` +- `0`. If not available, respond with '-'.\n\nText: {text}\n\nResponse:"
        # "emergence": "Extract and return only whether the species has a **larval stage** (emerges from the egg as a tadpole) or develops **directly** (emerges as a mini frog). Do not include any explanations, labels, or additional text. If not available, respond with '-'.\n\nText: {text}\n\nResponse:"
    }


    results = {}

    for key, prompt in prompts.items():
        response = client.chat.completions.create(
            model=os.getenv("MODEL_AZURE_ID"),
            messages=[
                {"role": "system", "content": prompt.format(text=text)}
            ],
            max_tokens=50,
            temperature=0.0,
        )
        results[key] = response.choices[0].message.content.strip()
    
    for field in ["male_svl", "female_svl", "avg_svl", "egg_diameter"]:
        if "+-" in results[field]:
            try: # current fix, but loses values
                avg, uncertainty = results[field].split("+-")
                results[field] = avg.strip()
                results[field + "_uncert"] = uncertainty.strip()
            except:
                print("ERROR, here is the reason: ")
                print(results[field])
                results[field] = '-'
                results[field + "_uncert"] = '-'
        else:
            results[field] = '-'
            results[field + "_uncert"] = '-'

    return results["male_svl"], results["male_svl_uncert"], results["female_svl"], results["female_svl_uncert"], results["avg_svl"], results["avg_svl_uncert"], results["min_clutch_size"], results["max_clutch_size"], results["egg_diameter"], results["egg_diameter_uncert"]

def run_all(genus, species):
    url = get_url(genus, species)
    xml_data = get_xml(url)

    if xml_data:
        if "NONEXISTENT PAGE" in xml_data: # page does not exist
            return "-", "-", "-", "-", "-", "-", "-", "-", "-", "-"

        return query_page(xml_data)
    
    # no data available
    return "-", "-", "-", "-", "-", "-", "-", "-", "-", "-"

def process_excel(file_path, output_file):
    try:
        xls = pd.ExcelFile(file_path)

        if "All Frogs" not in xls.sheet_names:
            raise ValueError("The 'All Frogs' sheet was not found in the Excel file.")

        df = xls.parse("All Frogs", header=1) # treat second row as headers

        if "Name" not in df.columns:
            raise ValueError("Could not find the 'Name' column under 'Name Stuff'.")
        
        results_df = pd.DataFrame(columns=["Name", "SVL Male (mm)", "+/- SVL Male (mm)", "SVL Female (mm)", "+/- SVL Female (mm)", "Avg SVL Adult (mm)", "+/- SVL Adult (mm)", "Min Egg Clutch", "Max Egg Clutch", "Avg Egg Diameter (mm)", "+/- Egg Diameter (mm)"])

        i = 1

        for index, row in df.iterrows():
            name = str(row["Name"]).strip() # genus species

            if " " not in name: # skip entries without a valid genus-species pair
                continue

            genus, species = name.split(" ", 1)
            print(f"Processing {i}: Genus={genus}, Species={species}")

            male_svl, male_svl_uncert, female_svl, female_svl_uncert, avg_svl, avg_svl_uncert, min_clutch_size, max_clutch_size, egg_diameter, egg_diameter_uncert = run_all(genus, species)

            results_df.loc[len(results_df)] = [name, male_svl, male_svl_uncert, female_svl, female_svl_uncert, avg_svl, avg_svl_uncert, min_clutch_size, max_clutch_size, egg_diameter, egg_diameter_uncert]
            i += 1

        results_df.to_excel(output_file, index=False)
        print(f"Results saved to {output_file}")

    except Exception as e:
        print(f"Error processing Excel file: {e}")
        
# input_file = input("Enter the path to the Excel file: ").strip()
input_file = "Froggy_Spreadsheet.xlsx"
output_file = "results.xlsx"

process_excel(input_file, output_file)
