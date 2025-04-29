# Data-Compilation-Model

## Project Overview
This project automates the extraction, compilation, and validation of biological and environmental data using large language models (LLMs) and open-source APIs.

It consists of two main components:
- **Frog-Specific Data Pipeline**: Focuses on amphibian data retrieval from **AmphibiaWeb**, **IUCN Red List**, and the **Climate Change Knowledge Portal** to extract species-level traits like **snout-vent length (SVL)**, **egg diameter**, **reproductive mode**, and associated **climate and altitude data**.
- **Generic Data Retrieval Framework**: A flexible, scalable system that supports querying **arbitrary species** using the IUCN Red List and climate APIs, allowing trait-specific extraction (e.g., **diet**, **habitat**, **average surface temperature**) using configurable prompt templates.

## Features
- **Frog-Specific Data Retrieval**: Extracts morphological, reproductive, and environmental data from AmphibiaWeb and IUCN APIs.
- **Machine Learning Model Extraction**: Uses OpenAI’s GPT-4o to extract structured values from unstructured text.
- **IUCN Red List API Integration**: Retrieves taxonomic and distribution information for any species.
- **Climate Change Knowledge Portal API Integration**: Collects temperature and rainfall data based on species range.
- **Generic Retrieval Framework**: Allows trait extraction for any species and feature, supporting batch processing and prompt customization.
- **Excel Output Generation**: Outputs processed and validated results to structured Excel files for downstream use.

## Required Dependencies
- At least Python 3
- Git
- Required libraries: `pandas`, `openpyxl`, `requests`, `bs4`, `dotenv`, `openai`, `selenium`