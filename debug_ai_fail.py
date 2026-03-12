from app import create_app
from models import StudyMaterial, db
from services.ai_service import AIService
import os

app = create_app()
ai = AIService()

with app.app_context():
    m = StudyMaterial.query.order_by(StudyMaterial.id.desc()).first()
    if m:
        print(f"Re-Processing material ID: {m.id}, Filename: {m.filename}")
        text = m.content_text[:15000]
        print(f"Text snippet: {text[:200]}")
        
        print("\n--- Summary Attempt ---")
        summary = ai.generate_summary(text)
        print(f"Summary result: {summary if summary else 'FAILED'}")
        
    else:
        print("No materials found")
