from services.ai_service import AIService
import os
from dotenv import load_dotenv

load_dotenv()
ai = AIService()

text = "Artificial intelligence (AI) is intelligence demonstrated by machines, as opposed to the natural intelligence displayed by animals including humans."

print("\n--- Testing Summary ---")
s = ai.generate_summary(text)
print(f"Summary: {s}")

print("\n--- Testing Flashcards ---")
f = ai.generate_flashcards(text)
print(f"Flashcards count: {len(f)}")
if f: print(f"Sample: {f[0]}")

print("\n--- Testing Learning Path ---")
p = ai.generate_learning_path(text)
print(f"Path count: {len(p)}")
if p: print(f"Sample: {p[0]}")
