import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get('GOOGLE_API_KEY')
genai.configure(api_key=api_key)

try:
    models = genai.list_models()
    with open('available_models.txt', 'w') as f:
        for m in models:
            f.write(f" - {m.name} ({m.supported_generation_methods})\n")
except Exception as e:
    with open('available_models.txt', 'w') as f:
        f.write(f"Error: {e}")
