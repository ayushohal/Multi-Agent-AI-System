# agents/email_agent.py
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

def process_email(email_content: str, intent=None, thread_id=None):
    """
    Analyze the email and extract structured info.
    """
    prompt = f"""
You are an email analysis assistant. Analyze the email below and extract the following:
- sender (if available)
- intent (e.g., Complaint, RFQ, Inquiry, Support)
- urgency (e.g., High, Medium, Low)
- summary

Format your response in this JSON format:
{{
  "sender": "example@example.com",
  "intent": "Complaint",
  "urgency": "High",
  "summary": "Customer is upset about a delayed shipment"
}}

Email Content:
{email_content}
"""

    raw_response = generate_response(prompt)
    cleaned_response = clean_llm_response(raw_response)

    try:
        response_dict = json.loads(cleaned_response)
    except Exception:
        response_dict = {"raw_response": cleaned_response}

    # Use intent from response if not provided externally
    detected_intent = intent or response_dict.get("intent", "Unknown")

    memory.log_entry(
        source="Email Agent",
        format="Email",
        intent=detected_intent,
        extracted_values=json.dumps(response_dict, indent=2),
        thread_id=thread_id
    )

    return response_dict
