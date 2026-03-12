import google.generativeai as genai
import os
from dotenv import load_dotenv
import time

load_dotenv()
genai.configure(api_key=os.environ.get('GOOGLE_API_KEY'))

model = genai.GenerativeModel('gemini-2.0-flash') # Trying 2.0 instead of 2.5
text = "Artificial intelligence (AI) is intelligence demonstrated by machines."

print("Calling Gemini 2.0 Flash...")
try:
    resp = model.generate_content(f"Summarize this: {text}")
    print(f"Success: {resp.text}")
except Exception as e:
    print(f"Error: {e}")

time.sleep(5) # Cooldown

model2 = genai.GenerativeModel('gemini-2.5-flash')
print("Calling Gemini 2.5 Flash...")
try:
    resp = model2.generate_content(f"Summarize this: {text}")
    print(f"Success: {resp.text}")
except Exception as e:
    print(f"Error: {e}")
