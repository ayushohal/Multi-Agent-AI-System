# agents/pdf_agent.py
import json
import re
from shared_memory.memory import SharedMemory
from utils.llm_utils import generate_response

memory = SharedMemory()

def clean_llm_response(text):
    """
    Remove markdown formatting like ```json ... ``` from the LLM response.
    """
    cleaned = re.sub(r"```json\s*(.*?)```", r"\1", text, flags=re.DOTALL).strip()
    cleaned = re.sub(r"```.*?```", "", cleaned, flags=re.DOTALL).strip()
    return cleaned

def process_pdf(content: str, intent=None, thread_id=None):
    """
    Analyze PDF content and extract:
    - document_type
    - key_topics
    - summary
    """
    prompt = f"""
You are a document analysis assistant. Given the PDF content below, extract the following:
- document_type (e.g., Invoice, Report, Contract, Resume)
- key_topics (a list of 3-5 keywords or topics)
- summary (brief description of the document)

Return your response strictly in the following JSON format:
{{
  "document_type": "Invoice",
  "key_topics": ["payment", "services", "invoice number"],
  "summary": "This is an invoice for web development services provided in May 2025."
}}

PDF Content:
{content[:2000]}
"""

    raw_response = generate_response(prompt)
    cleaned_response = clean_llm_response(raw_response)

    try:
        response_dict = json.loads(cleaned_response)
    except Exception:
        response_dict = {"raw_response": cleaned_response}

    # Log the cleaned dictionary (not quoted text)
    memory.log_entry(
        source="PDF Agent",
        format="PDF",
        intent=intent,
        extracted_values=json.dumps(response_dict, indent=2),
        thread_id=thread_id
    )

    return response_dict
