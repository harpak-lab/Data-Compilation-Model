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

def query_model(text, prompts):

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    prompt_templates = {
        "list": "Extract and return only the {var} from the following text. Output the {var} as a single comma-separated list on one line with no line breaks or bullet points. Do not include any explanations, descriptions, or additional information. If not available, respond with '-'.",
        "number": "Extract and return only the {var} from the following text. Do not include any explanations, descriptions, or additional information—just a number and unit. If not available, respond with '-'."
    }

    results = {}

    for var_name, var_type in prompts.items():
        prompt = prompt_templates[var_type].format(var=var_name)

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"{prompt}\n\nText: {text}"}
            ],
            temperature=0.0,
            max_tokens=150
        )
        results[var_name.capitalize()] = response.choices[0].message.content.strip()

    return results

if __name__ == "__main__":
    animal_list = ["Mus musculus", "Herichthys cyanoguttatus", "Coris julis", "Lagothrix lagothricha", "Bombus impatiens", "Turdis migratorius", "Ambystoma maculatum"]

    prompts = {
        "habitats and specific countries": "list",
        "diet": "list",
        "size (length or weight)": "number"
    }

    features = [f.capitalize() for f in prompts.keys()]
    results_df = pd.DataFrame(columns=["Name"] + features)

    for a in animal_list:
        genus, species = a.split()

        print(f"Processing {genus} {species}")

        iucn_info = get_iucn_info(genus, species)

        if iucn_info is None:
            results_df = pd.concat([results_df, pd.DataFrame([[a] + ["-"] * len(features)], columns=results_df.columns)], ignore_index=True)
            continue

        result_dict = query_model(iucn_info, prompts)
        result_row = [a] + [result_dict.get(feature, "-") for feature in features]

        results_df = pd.concat([results_df, pd.DataFrame([result_row], columns=results_df.columns)], ignore_index=True)

    results_df.to_excel("results/generic_retrieval_results.xlsx", index=False)