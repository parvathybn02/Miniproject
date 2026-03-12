import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.environ.get('GOOGLE_API_KEY'))

models_to_try = [
    'gemini-1.5-flash-latest',
    'gemini-2.0-flash-lite',
    'gemini-pro',
    'gemini-1.5-pro'
]

for m_name in models_to_try:
    print(f"Trying {m_name}...")
    try:
        model = genai.GenerativeModel(m_name)
        resp = model.generate_content("Say hello")
        print(f"Success with {m_name}: {resp.text}")
        break
    except Exception as e:
        print(f"Failed {m_name}: {e}")
