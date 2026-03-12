import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.environ.get('GOOGLE_API_KEY'))
try:
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Say hello")
    print(f"Gemini-pro: {response.text}")
except Exception as e:
    print(f"Gemini-pro error: {e}")
    
try:
    model = genai.GenerativeModel('gemini-1.5-pro')
    response = model.generate_content("Say hello")
    print(f"Gemini-1.5-pro: {response.text}")
except Exception as e:
    print(f"Gemini-1.5-pro error: {e}")
