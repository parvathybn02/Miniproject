import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.environ.get('GOOGLE_API_KEY'))
try:
    models = genai.list_models()
    for m in models:
        print(f"Model ID: {m.name}, Display Name: {m.display_name}, Methods: {m.supported_generation_methods}")
except Exception as e:
    print(f"Error listing: {e}")
