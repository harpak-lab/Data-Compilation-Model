import sys
import os
import openai
import time
from openai import OpenAI
import pandas as pd
from dotenv import load_dotenv
from species_info_utils import get_assessment_id, get_species_assessment, find_location, get_data

load_dotenv()

def get_cckp_info(assessment_info):
    cckp_info = None
    if "locations" in assessment_info:
        # grab location data from species info
        locations = [loc["description"]["en"] for loc in assessment_info["locations"]]
        if locations:
            cckp_info = []
            codes = find_location(locations)
            for code in codes:
                if code:
                    data = get_data(code)
                    if data:
                        cckp_info.append(data)
    return cckp_info

def get_info(genus, species, need_iucn, need_cckp):
    iucn_info, cckp_info = None, None

    assessment_id = get_assessment_id(genus, species)
    if assessment_id:
        assessment_info = get_species_assessment(assessment_id)
        if need_iucn:
            iucn_info = assessment_info
        if need_cckp:
            cckp_info = get_cckp_info(assessment_info)
    else:
        print("No info found")

    if cckp_info == []:
        cckp_info = None

    return iucn_info, cckp_info

def safe_openai_chat_completion(client, model, messages, temperature=0.0, max_tokens=150):
    while True:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response
        except openai.RateLimitError as e:
            print(f"OpenAI RateLimitError: {e}. Waiting before retrying...")
            time.sleep(60)
        except Exception as e:
            print(f"OpenAI API error: {e}")
            raise e


def query_model(iucn_text, cckp_text, prompts):

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    prompt_templates = {
        "list": "Extract and return only the {var} from the following text. Output the {var} as a single comma-separated list on one line with no line breaks or bullet points. Do not include any explanations, descriptions, or additional information. If not available, respond with '-'.",
        "number": "Extract and return only the {var} from the following text. If there are multiple values, average them. Do not include any explanations, descriptions, or additional information—just a number and unit. If not available, respond with '-'."
    }

    results = {}

    if isinstance(cckp_text, list):
        cckp_text = "\n\n".join([str(entry) for entry in cckp_text]) # flatted cckp from list of json objects to string

    for var_name, var_type in prompts.items():

        prompt = prompt_templates[var_type[0]].format(var=var_name)
        text = iucn_text if var_type[1] == "iucn" else cckp_text

        if text is None: # model doesn't have info for this field
            results[var_name.capitalize()] = "-"
            continue
            
        # response = client.chat.completions.create(
        #     model="gpt-4o",
        #     messages=[
        #         {"role": "system", "content": "You are a helpful assistant."},
        #         {"role": "user", "content": f"{prompt}\n\nText: {text}"}
        #     ],
        #     temperature=0.0,
        #     max_tokens=150
        # )

        response = safe_openai_chat_completion(
            client,
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
        "habitats and specific countries": ("list", "iucn"),
        "diet": ("list", "iucn"),
        "size (length or weight)": ("number", "iucn"),
        "average annual surface temperature (tas)": ("number", "cckp")
    }

    features = [f.capitalize() for f in prompts.keys()]
    results_df = pd.DataFrame(columns=["Name"] + features)

    for a in animal_list:
        genus, species = a.split()

        print(f"Processing {genus} {species}")

        # make a list containing the second item in each tuple in prompts
        prompts_2nd_vals = [item[1] for item in prompts.values()]
    
        iucn_info, cckp_info = get_info(genus, species, "iucn" in prompts_2nd_vals, "cckp" in prompts_2nd_vals)

        # we need iucn and iucn is not available, and we dont need cckp
        if ((iucn_info is None) and ("iucn" in prompts_2nd_vals)) and ("cckp" not in prompts_2nd_vals):
            results_df = pd.concat([results_df, pd.DataFrame([[a] + ["-"] * len(features)], columns=results_df.columns)], ignore_index=True)
            continue

        # we need cckp and cckp is not available, and we dont need iucn
        if ((cckp_info is None) and ("cckp" in prompts_2nd_vals)) and ("iucn" not in prompts_2nd_vals):
            results_df = pd.concat([results_df, pd.DataFrame([[a] + ["-"] * len(features)], columns=results_df.columns)], ignore_index=True)
            continue

        # we need both and both aren't available
        if ((iucn_info is None) and ("iucn" in prompts_2nd_vals)) and (cckp_info is None and ("cckp" in prompts_2nd_vals)):
            results_df = pd.concat([results_df, pd.DataFrame([[a] + ["-"] * len(features)], columns=results_df.columns)], ignore_index=True)
            continue

        result_dict = query_model(iucn_info, cckp_info, prompts)
        result_row = [a] + [result_dict.get(feature, "-") for feature in features]

        results_df = pd.concat([results_df, pd.DataFrame([result_row], columns=results_df.columns)], ignore_index=True)

    results_df.to_excel("02_generic_data_compilation/results/generic_retrieval_results.xlsx", index=False)