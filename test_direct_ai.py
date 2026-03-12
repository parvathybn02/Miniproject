from services.ai_service import AIService
import os
from dotenv import load_dotenv

load_dotenv()
print("Starting AIService...")
ai = AIService()
print("Service initialized.")

text = "This is a test of the AI content generation system."
print("Generating summary...")
s = ai.generate_summary(text)
print(f"Summary: {s}")
