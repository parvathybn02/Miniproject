from app import create_app
from extensions import db
from models import StudyMaterial, ExamBooster
from services.ai_service import AIService
import json

app = create_app()
with app.app_context():
    material = StudyMaterial.query.get(3)
    if not material:
        print("Material 3 not found")
        exit()
    
    print(f"Testing Booster for: {material.filename}")
    ai_service = AIService()
    text = material.content_text[:15000] if material.content_text else ""
    
    if not text:
        print("Empty text!")
        exit()
        
    print(f"Text length: {len(text)}")
    print("Calling generate_exam_booster...")
    
    data = ai_service.generate_exam_booster(text)
    if data:
        print("SUCCESS!")
        print(f"Notes: {data.get('revision_notes')[:100]}...")
        print(f"Questions: {len(data.get('probable_questions', []))}")
        
        # Save it to DB for user
        new_booster = ExamBooster(
            material_id=3,
            revision_notes=data.get('revision_notes', ''),
            probable_questions=data.get('probable_questions', [])
        )
        db.session.add(new_booster)
        db.session.commit()
    else:
        print("FAILED to generate booster content.")
