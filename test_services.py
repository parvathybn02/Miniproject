from services.ocr_service import OCRService
from services.ai_service import AIService
import os
from dotenv import load_dotenv

load_dotenv()

def test():
    print("Testing AIService...")
    ai = AIService()
    summary = ai.generate_summary("This is a test document about artificial intelligence.")
    print(f"Summary: {summary}")
    
    flashcards = ai.generate_flashcards("This is a test document about artificial intelligence.")
    print(f"Flashcards: {flashcards}")
    
    path = ai.generate_learning_path("This is a test document about artificial intelligence.")
    print(f"Path: {path}")

if __name__ == "__main__":
    test()
