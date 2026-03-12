import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.environ.get('GOOGLE_API_KEY'))
try:
    model = genai.GenerativeModel('models/gemini-1.5-flash')
    response = model.generate_content("Generate a summary of: The Earth is round.")
    print(f"Success! Gemini-1.5-flash: {response.text}")
except Exception as e:
    print(f"Gemini-1.5-flash error: {e}")
