import json
import re
from shared_memory.memory import SharedMemory
from utils.llm_utils import generate_response

memory = SharedMemory()

INVOICE_TARGET_SCHEMA_FIELDS = ["invoice_number", "date", "customer_name", "items", "total_amount"]
COMPLAINT_TARGET_SCHEMA_FIELDS = ["complaint_id", "order_id", "customer_name", "date", "message", "urgency"]

def clean_llm_response(text):
    cleaned = re.sub(r"```json\s*(.*?)```", r"\1", text, flags=re.DOTALL).strip()
    cleaned = re.sub(r"```.*?```", "", cleaned, flags=re.DOTALL).strip()
    return cleaned

def process_json(json_content, intent=None, thread_id=None):
    """
    Process JSON content with intent passed explicitly.
    """
    try:
        if isinstance(json_content, str):
            data = json.loads(json_content)
        elif isinstance(json_content, dict):
            data = json_content
        else:
            raise ValueError("Invalid JSON format. Input must be a string or dict.")
    except Exception as e:
        return {
            "error": f"Failed to parse JSON content. Error: {str(e)}"
        }

    if intent is None:
        # Fallback: get intent from JSON or default
        intent = data.get("intent", "Unknown")

    missing_fields = []
    anomalies = []

    if intent == "Invoice":
        missing_fields = [field for field in INVOICE_TARGET_SCHEMA_FIELDS if field not in data or not data[field]]

        try:
            items = data.get("items", [])
            total_amount = data.get("total_amount", 0)
            calculated_total = sum(item["quantity"] * item["price"] for item in items)
            if calculated_total != total_amount:
                anomalies.append(f"Total mismatch: expected {calculated_total}, found {total_amount}")
        except Exception:
            anomalies.append("Error calculating total from items.")

        target_fields = INVOICE_TARGET_SCHEMA_FIELDS

    elif intent == "Complaint":
        missing_fields = [field for field in COMPLAINT_TARGET_SCHEMA_FIELDS if field not in data or not data[field]]

        message = data.get("message", "").lower()
        urgency = data.get("urgency", "").lower()
        if urgency == "low" and any(word in message for word in ["refund", "damaged", "legal", "escalate"]):
            anomalies.append("Urgency marked 'Low' but message seems serious.")

        target_fields = COMPLAINT_TARGET_SCHEMA_FIELDS

    else:
        anomalies.append(f"Intent '{intent}' is not recognized for validation.")
        target_fields = []

    prompt = f"""
You are a JSON validation assistant.

Given this JSON input, validate it against the schema:
{target_fields}

Instructions:
- Do NOT modify or overwrite any fields.
- Identify missing fields and data anomalies only.
- Return a minimal JSON with three keys:
  {{
    "missing_fields": [...],
    "anomalies": [...],
    "original_json": <exact JSON input>
  }}
- No extra text outside the JSON.

JSON Input:
{json.dumps(data, indent=2)}
"""

    llm_response = generate_response(prompt)
    cleaned_response = clean_llm_response(llm_response)

    try:
        parsed_llm = json.loads(cleaned_response)
        original_json = parsed_llm.get("original_json", data)
    except Exception:
        original_json = data

    memory.log_entry(
        source="JSON Agent",
        format="JSON",
        intent=intent,
        extracted_values=json.dumps({
            "missing_fields": missing_fields,
            "anomalies": anomalies,
            "original_json": original_json
        }, indent=2),
        thread_id=thread_id
    )

    return {
        "missing_fields": missing_fields,
        "anomalies": anomalies,
        "llm_response": cleaned_response
    }
