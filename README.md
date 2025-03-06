# Data-Compilation-Model

## Project Overview
This project automates the extraction, compilation, and validation of biological data related to frog species. It processes information from **AmphibiaWeb**, **IUCN Red List** and **Climate Change Knowledge Portal**, extracting details such as **snout-vent length (SVL), egg diameter, and environmental data**.

## Features
- **Automated Data Retrieval:** Fetches XML data from AmphibiaWeb for a given species.
- **Machine Learning Model Extraction:** Uses an internal large language model (LLM) to extract biological details.
- **IUCN Red List API Integration:** Retrieves species location data through API queries.
- **Climate Change Knowledge Portal API Integration:** Fetches temperature and rainfall data for species locations.
- **Excel Output Generation:** Saves validated data to a structured Excel file.

## Required Dependencies
- At least Python 3
- Git
- Required libraries: `pandas`, `openpyxl`, `requests`, `bs4`, `dotenv`, `openai`
