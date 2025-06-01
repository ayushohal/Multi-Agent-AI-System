import os
import sys
import uuid
from agents.classifier_agent import classify_input, extract_text
from agents.json_agent import process_json
from agents.email_agent import process_email
from shared_memory.memory import SharedMemory

memory = SharedMemory()

def main():
    # Get file path from command line argument or use default
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "sample_inputs/sample_email.txt"

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    # Generate a unique thread ID to link related log entries
    thread_id = str(uuid.uuid4())

    # Classify the input file to determine format and intent
    input_type, intent = classify_input(file_path, thread_id=thread_id)
    print(f"Classified format: {input_type}, intent: {intent}")

    # Log the classification result with thread_id
    memory.log_entry(
        source=os.path.basename(file_path),
        format=input_type,
        intent=intent,
        extracted_values="None",
        thread_id=thread_id
    )

    # Extract content from the file
    content = extract_text(file_path)

    # Route to appropriate agent based on format, passing thread_id
    if input_type == "JSON":
        result = process_json(content, intent=intent, thread_id=thread_id)
    elif input_type == "Email":
        result = process_email(content, intent=intent, thread_id=thread_id)
    elif input_type == "PDF":
        from agents.pdf_agent import process_pdf
        result = process_pdf(content, intent=intent, thread_id=thread_id)
    else:
        result = {"error": f"Unsupported format: {input_type}"}

    print("Processing result:")
    print(result)

if __name__ == "__main__":
    main()
