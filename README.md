# Multi-Agent-AI-System
This repository contains a multi-agent AI system designed to classify, analyze, and process various document formats including PDFs, JSON files, and emails. The system leverages specialized agents for each format, integrates with a shared memory database for contextual logging, and uses large language models for intelligent content understanding.

## Features
- Classifies input files into JSON, PDF, or Email
- Processes JSON invoices and complaints with schema validation by missing fields and anomaly detection
- Extracts and summarizes PDF documents using AI
- Analyzes email content for intent, sender, urgency, and summary
- Logs results into a shared SQLite database (`memory.db`)
- Includes shared memory module to persist conversation logs

## Folder Structure

- `agents/`: Contains the AI agent modules
- `shared_memory/`: SQLite-backed shared memory for logging
- `utils/`: Utility functions for interacting with LLM API
- `sample_inputs/`: Example input files for testing
- `logs/`: Sample output logs
- `main.py`: Main script to run the system

## Setup

1. Create and activate your Python virtual environment:
   python -m venv venv
   .\venv\Scripts\activate
   
2. Install dependencies:
   pip install -r requirements.txt
   Ensure you have your API keys configured for the LLM service as required by utils/llm_utils.py.

3. Usage
   Run the main script with the path to an input file:
   python main.py sample_inputs/sample_pdf1.pdf

4. Sample Inputs
   Sample input files are stored in sample_inputs folder with .json, .pdf, .txt extensions for json, pdf and email samples respectively.

5. Logs and Output
   Processed results and logs are saved in the memory.db SQLite database and can be viewed using any SQLite viewer. Sample output logs are stored in logs/
