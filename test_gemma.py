import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.environ.get('GOOGLE_API_KEY'))

try:
    model = genai.GenerativeModel('gemma-3-4b-it')
    resp = model.generate_content("Say hello")
    print(f"SUCCESS with Gemma: {resp.text}")
except Exception as e:
    print(f"FAILED with Gemma: {e}")
