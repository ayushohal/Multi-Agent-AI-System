import os
import json
import pdfplumber
from shared_memory.memory import SharedMemory
from utils.llm_utils import generate_response

memory = SharedMemory()

def detect_format(file_path):
    if file_path.endswith(".json"):
        return "JSON"
    elif file_path.endswith(".pdf"):
        return "PDF"
    elif file_path.endswith(".txt"):
        return "Email"
    else:
        return "Unknown"

def extract_text(file_path):
    format_type = detect_format(file_path)
    if format_type == "PDF":
        with pdfplumber.open(file_path) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    elif format_type in ["JSON", "Email"]:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()  # strip to remove accidental whitespace
    return ""

def clean_and_parse_json(raw_text):
    import re
    # Remove markdown json code blocks if any
    cleaned = re.sub(r"```json\s*(.*?)```", r"\1", raw_text, flags=re.DOTALL).strip()
    cleaned = re.sub(r"```(.*?)```", r"\1", cleaned, flags=re.DOTALL).strip()
    return json.loads(cleaned)

def classify_input(file_path, thread_id=None):
    content = extract_text(file_path)
    format_type = detect_format(file_path)

    prompt = f"""
You are a classification agent. Given the content below, return a JSON object **only**, strictly following this format:
{{
  "format": "PDF",  // or "JSON", or "Email"
  "intent": "Invoice"  // or "Company Profile", "Complaint", "RFQ", "Company Profile", "Brochure", "Report", "Contract", "Unknown", "Inquiry", etc.
}}

Your response must be valid JSON only with no extra text, no explanations, and no markdown.

Content:
{content[:2000]}
"""

    result = generate_response(prompt)

    try:
        classification = clean_and_parse_json(result)
    except Exception as e:
        print(f"Could not parse classification output, defaulting. Error: {e}")
        classification = {"format": format_type, "intent": "Unknown"}

    return classification.get("format", format_type), classification.get("intent", "Unknown")

def route_to_agent(format_type):
    if format_type == "JSON":
        return "json_agent"
    elif format_type == "Email":
        return "email_agent"
    elif format_type == "PDF":
        return "pdf_agent"  # Placeholder for future implementation
    else:
        return "unknown_agent"
