import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load your .env file to get the Gemini API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)

# Create a Gemini model instance
model = genai.GenerativeModel("models/gemini-1.5-flash-8b-001")


def generate_response(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"❌ Error from Gemini API: {e}")
        return "Error generating response"
