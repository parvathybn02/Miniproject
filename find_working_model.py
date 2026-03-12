import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.environ.get('GOOGLE_API_KEY'))
try:
    print("Listing all models...")
    for m in genai.list_models():
        print(f"Name: {m.name}, Methods: {m.supported_generation_methods}")
        if 'generateContent' in m.supported_generation_methods:
            print(f"Attempting with {m.name}...")
            model = genai.GenerativeModel(m.name)
            resp = model.generate_content("Say hello")
            print(f"Success with {m.name}: {resp.text}")
            break
except Exception as e:
    print(f"Error overall: {e}")
