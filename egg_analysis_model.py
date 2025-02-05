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

    # prompt = (
    #     "You are an assistant analyzing frog data. Extract and return the following information from the text, in the requested unit:\n"
    #     "1. Male and Female SVL (mm): snout-vent length in MILLIMETERS.\n"
    #     "2. Egg clutch capacity (eggs): number of eggs in one clutch in UNITS OF EGGS.\n"
    #     "3. Average egg diameter (mm): size of eggs in MILLIMETERS.\n"
    #     "4. Emergence: whether the species has a larval stage (emerges from the egg as a tadpole) or develops directly (emerges as a mini frog).\n\n"
    #     "Do not confuse egg clutch capacity and average egg diameter. Do not provide any additional context or explanation.\n\n"
    #     "If any of the information is not available, respond with '-'.\n\n"
    #     f"Text: {text}\n\n"
    #     "Response:"
    # )

    prompt = (
        "You are an assistant analyzing frog data. Extract and return the following information from the text, strictly adhering to the specified units:\n"
        "1. **Male and Female SVL (mm):** Snout-vent length in **MILLIMETERS (mm)**.\n"
        "2. **Egg clutch size (number of eggs):** The **total number of eggs laid per clutch**, expressed as a **whole number** or a **range of numbers**, in **UNITS OF EGGS**.\n"
        "3. **Average egg diameter (mm):** The **size of an individual egg**, measured in **MILLIMETERS (mm)**. Do not provide the number of eggs here.\n"
        "4. **Emergence:** Whether the species has a **larval stage** (emerges from the egg as a tadpole) or develops **directly** (emerges as a mini frog).\n\n"

        "**STRICT INSTRUCTIONS:**\n"
        "- **Egg clutch size must always be a whole number or a range of numbers followed by the word 'eggs'** (e.g., '50 eggs', '200-300 eggs').\n"
        "- **Egg diameter must always be a number followed by 'mm'** (e.g., '3.5 mm', '5.2 mm').\n"
        "- **Egg clutch size CANNOT be measured in millimeters (mm), and egg diameter CANNOT be measured in eggs.**\n"
        "- If you find a value and are unsure whether it refers to egg diameter or clutch size, check the unit:\n"
        "  - If the unit is **'mm'**, it belongs in egg diameter.\n"
        "  - If the unit is **'eggs'**, it belongs in clutch size.\n"
        "- Do not place 'eggs' in the diameter column and do not place 'mm' in the clutch size column.\n"
        "- **If a value is missing, return '-' exactly. Do not make assumptions.**\n"
        "- **Do not provide any additional context or explanation. Only return the extracted values.**\n\n"

        f"Text: {text}\n\n"
        "Response:"
    )


    response = client.chat.completions.create(
        model=os.getenv("MODEL_AZURE_ID"),
        messages=[
            {"role": "system", "content": prompt}
            ],
        max_tokens=150,
        temperature=0.0,
    )
    result = response.choices[0].message.content.strip()

    try:
        lines = [line.split(":", 1)[-1].strip() for line in result.split("\n") if ":" in line]

        # TEMP SOLUTION TO GET LINES RIGHT
        svl = lines[0].replace("**", "").strip()
        lines.remove(lines[0])

        # svl = next((line for line in lines if "mm" in line and "svl" in line.lower()), "-")
        clutch_size = next((line.replace("**", "").strip() for line in lines if "eggs" in line.lower()), "-")
        egg_diameter = next((line.replace("**", "").strip() for line in lines if "mm" in line and "eggs" not in line.lower()), "-")
        # emergence = next((line for line in lines if "emergence" in line.lower()), "-")
        emergence = lines[2].replace("**", "").strip()

    except Exception as e:
        print(f"Error parsing model response: {e}")
        svl, clutch_size, egg_diameter, emergence = "-", "-", "-", "-"

    return svl, clutch_size, egg_diameter, emergence

def run_all(genus, species):
    url = get_url(genus, species)
    xml_data = get_xml(url)
    if xml_data:
        if "NONEXISTENT PAGE" in xml_data:
            return "Page does not exist.", "Page does not exist.", "Page does not exist.", "Page does not exist."

        return query_page(xml_data)
    return "No data available", "No data available", "No data available", "No data available"

def process_excel(file_path, output_file):
    try:
        xls = pd.ExcelFile(file_path)

        if "All Frogs" not in xls.sheet_names:
            raise ValueError("The 'All Frogs' sheet was not found in the Excel file.")

        df = xls.parse("All Frogs", header=1) # treat second row as headers

        if "Name" not in df.columns:
            raise ValueError("Could not find the 'Name' column under 'Name Stuff'.")
        
        results_df = pd.DataFrame(columns=["Name", "Male/Female SVL", "Egg Clutch Size", "Average Egg Diameter", "Emergence"])

        i = 1

        for index, row in df.iterrows():
            name = str(row["Name"]).strip()  # Genus species
            if " " not in name:  # Skip entries without a valid genus-species pair
                continue

            genus, species = name.split(" ", 1)
            print(f"Processing {i}: Genus={genus}, Species={species}")

            svl, clutch_size, egg_diameter, emergence = run_all(genus, species)

            results_df.loc[len(results_df)] = [name, svl, clutch_size, egg_diameter, emergence]
            i += 1

        results_df.to_excel(output_file, index=False)
        print(f"Results saved to {output_file}")

    except Exception as e:
        print(f"Error processing Excel file: {e}")
        
# input_file = input("Enter the path to the Excel file: ").strip()
input_file = "Froggy_Spreadsheet.xlsx"
output_file = "results.xlsx"

process_excel(input_file, output_file)
