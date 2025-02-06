# Data-Compilation-Model

## Project Overview
This project automates the extraction, compilation, and validation of biological data related to frog species. It processes species information from **AmphibiaWeb**, extracts details such as **snout-vent length (SVL), egg clutch size, and egg diameter**.

## Features
- **Automated Data Retrieval:** Fetches XML data from AmphibiaWeb for a given species.
- **Machine Learning Model Extraction:** Uses an internal large language model (LLM) to extract biological details.
- **Excel Output Generation:** Saves validated data to a structured Excel file.

## Required Dependencies
- At least Python 3
- Git
- Required libraries: `pandas`, `openpyxl`, `requests`, `bs4`, `dotenv`, `openai`
