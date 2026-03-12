from app import create_app
from models import StudyMaterial, Flashcard, Quiz, db
import json

app = create_app()
with app.app_context():
    materials = StudyMaterial.query.all()
    print(f"Total Materials: {len(materials)}")
    for m in materials:
        print(f"ID: {m.id}, File: {m.filename}, Text Len: {len(m.content_text) if m.content_text else 0}")
        print(f"  Summary: {'Present' if m.summary else 'None'}")
        print(f"  Learning Path: {'Present' if m.learning_path else 'None'}")
        
    flashcards = Flashcard.query.all()
    print(f"Total Flashcards: {len(flashcards)}")
    
    quizzes = Quiz.query.all()
    print(f"Total Quizzes: {len(quizzes)}")
