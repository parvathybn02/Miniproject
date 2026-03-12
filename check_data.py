from app import create_app
from models import StudyMaterial
app = create_app()
with app.app_context():
    m = StudyMaterial.query.order_by(StudyMaterial.id.desc()).first()
    if m:
        print(f"ID: {m.id}")
        print(f"Filename: {m.filename}")
        print(f"Text length: {len(m.content_text) if m.content_text else 0}")
        print(f"Content start: {m.content_text[:100] if m.content_text else 'EMPTY'}")
        print(f"Summary length: {len(m.summary) if m.summary else 0}")
        print(f"Path length: {len(m.learning_path) if m.learning_path else 0}")
    else:
        print("No materials found")
