from services.ai_service import AIService
import os
from dotenv import load_dotenv

load_dotenv()
print("Starting AIService...")
ai = AIService()
print(f"Service initialized with model: {ai.google_model.model_name}")

text = "Artificial intelligence (AI) is intelligence demonstrated by machines, as opposed to the natural intelligence displayed by animals including humans."
print("\n--- Testing Flashcards (JSON) ---")
f = ai.generate_flashcards(text)
print(f"Flashcards count: {len(f)}")
if f:
    print(f"Sample Card: {f[0]}")
else:
    print("FAILED to generate flashcards.")
