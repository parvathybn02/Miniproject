import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.environ.get('GOOGLE_API_KEY'))

model = genai.GenerativeModel('gemma-3-4b-it')
config = genai.GenerationConfig(response_mime_type="application/json")

prompt = "Generate 2 flashcards in JSON format: {'flashcards': [{'question': '...', 'answer': '...'}]}"

try:
    resp = model.generate_content(prompt, generation_config=config)
    print(f"SUCCESS JSON: {resp.text}")
except Exception as e:
    print(f"FAILED JSON: {e}")
