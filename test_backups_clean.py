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

results = []
for m_name in models_to_try:
    try:
        model = genai.GenerativeModel(m_name)
        resp = model.generate_content("Say hello")
        results.append(f"SUCCESS: {m_name} -> {resp.text}")
        break
    except Exception as e:
        results.append(f"FAILED: {m_name} -> {str(e)[:100]}")

with open('backups_final.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(results))
