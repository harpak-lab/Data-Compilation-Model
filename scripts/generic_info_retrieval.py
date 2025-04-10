import os
import openai
from openai import OpenAI
import pandas as pd
from dotenv import load_dotenv
from froggy_vars.temp_and_rainfall import get_assessment_id, get_species_assessment

load_dotenv()

def get_iucn_info(genus, species):
    assessment_id = get_assessment_id(genus, species)
    if assessment_id:
        assessment_info = get_species_assessment(assessment_id)
        return assessment_info
    print("No iucn info found")
    return None

def query_model(text):

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    prompts = {
        "habitat": "Extract and return only the habitats and specific countries from the following text. Output the habitats and countries as a single comma-separated list on one line with no line breaks or bullet points. Do not include any explanations, descriptions, or additional information. If not available, respond with '-'.",
        "diet": "Extract and return only the diet from the following text. Output the diet as a single comma-separated list on one line with no line breaks or bullet points. Do not include any explanations, descriptions, or additional information—just a plain list. If not available, respond with '-'.",
        "size": "Extract and return only the size from the following text. This may be length or weight depending on what is available. Do not include any explanations, descriptions, or additional information—just a number and unit. If not available, respond with '-'.",
        # "temp": "Extract and return only the average annual temperature of the area this species is found in. Do not include any explanations, descriptions, or additional information—just a number and unit. If not available, respond with '-'."
    }

    '''
    the above should become something like:
    prompts = {
        "habitat": "list",
        "diet": "list",
        "size": "number",
    }
    '''

    results = {}

    for key, instruction in prompts.items():
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"{instruction}\n\nText: {text}"}
            ],
            temperature=0.0,
            max_tokens=150  # increase if needed
        )
        results[key] = response.choices[0].message.content.strip()

    return results["habitat"], results["diet"], results["size"]

if __name__ == "__main__":
    animal_list = ["Mus musculus", "Herichthys cyanoguttatus", "Coris julis", "Lagothrix lagothricha", "Bombus impatiens", "Turdis migratorius", "Ambystoma maculatum"]
    features = ["Habitat", "Diet", "Size"]

    results_df = pd.DataFrame(columns=["Name"] + features)

    for a in animal_list:
        genus, species = a.split()

        print(f"Processing {genus} {species}")

        iucn_info = get_iucn_info(genus, species)

        if iucn_info is None:
            results_df = pd.concat([results_df, pd.DataFrame([[a] + ["-"] * len(features)], columns=results_df.columns)], ignore_index=True)
            continue

        habitat, diet, size = query_model(iucn_info)

        results_df = pd.concat([results_df, pd.DataFrame([[a, habitat, diet, size]], columns=results_df.columns)], ignore_index=True)
    
    results_df.to_excel("results/generic_retrieval_results.xlsx", index=False)