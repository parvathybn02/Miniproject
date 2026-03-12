import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get('GOOGLE_API_KEY')
print(f"API Key: {api_key[:5]}...{api_key[-5:]}")
genai.configure(api_key=api_key)

try:
    models = genai.list_models()
    print("Available Models:")
    for m in models:
        print(f" - {m.name} ({m.supported_generation_methods})")
except Exception as e:
    print(f"Error: {e}")
