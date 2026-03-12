from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
import os
from werkzeug.utils import secure_filename
from extensions import db
from models import StudyMaterial, Flashcard, Quiz, ExamBooster, QuizResult
from services.ocr_service import OCRService
from services.ai_service import AIService

api_bp = Blueprint('api', __name__)
ai_service = AIService()

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api_bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        import time
        filename = f"{int(time.time())}_{filename}"
        
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        print(f"File saved: {filename}. ID being created...")

        # Create base record (content_text will be extracted in process step)
        material = StudyMaterial(filename=filename, user_id=current_user.id, content_text="")
        db.session.add(material)
        db.session.commit()

        return jsonify({'message': 'Upload successful', 'id': material.id})

    return jsonify({'error': 'File type not allowed'}), 400

@api_bp.route('/process/<int:id>', methods=['POST'])
@login_required
def process_material(id):
    material = StudyMaterial.query.get_or_404(id)
    if material.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    print(f"Processing material {id}...")
    
    # 1. Extract Text (if not already done)
    if not material.content_text or len(material.content_text) < 5:
        ext = material.filename.rsplit('.', 1)[1].lower()
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], material.filename)
        content_text = ""
        
        print(f"Extracting text from {ext} in background...")
        try:
            if ext == 'txt':
                with open(filepath, 'r', encoding='utf-8') as f:
                    content_text = f.read()
            elif ext == 'pdf':
                content_text = OCRService.extract_text_from_pdf(filepath)
            elif ext in ['png', 'jpg', 'jpeg']:
                content_text = OCRService.extract_text_from_image(filepath)
            
            if not content_text or len(content_text.strip()) < 5:
                # Fallback hint for empty/encrypted files
                content_text = "The file was empty or content could not be extracted. Please ensure it is a text-based document or high-quality image."
            
            material.content_text = content_text
            db.session.commit()
            print(f"Extraction complete for {id}. Length: {len(content_text)}")
        except Exception as e:
            print(f"Background Extraction Error: {e}")
            return jsonify({'error': 'Failed to extract text from file.'}), 500

    # Increase context for more detailed results
    text = material.content_text[:15000] 
    
    try:
        import time
        # 1. Generate Summary
        print("Generating summary...")
        summary = ai_service.generate_summary(text)
        if summary and "failed" not in summary.lower():
            material.summary = summary
            db.session.commit()
            print(f"Summary saved for material {id}.")
        else:
            print(f"Summary was totally empty or failed for {id}.")
            material.summary = "Summary generation failed. The AI might be busy or your material could not be processed."
            db.session.commit()
        
        time.sleep(5) # Small pause for rate limit safety
        
        # 2. Generate Learning Path
        print("Generating learning path...")
        path = ai_service.generate_learning_path(text)
        if path:
            material.learning_path = path
            db.session.commit()
            print(f"Learning path generated with {len(path)} modules.")
        else:
            print("Learning path was empty! Using fallback.")
            material.learning_path = [{"title": "Introduction", "description": "Overview of the uploaded material.", "difficulty": "easy"}]
            db.session.commit()
        
        time.sleep(5)

        # 3. Flashcards
        print("Generating flashcards...")
        flashcards_data = ai_service.generate_flashcards(text)
        if flashcards_data:
            for card in flashcards_data:
                new_card = Flashcard(
                    question=card['question'], answer=card['answer'],
                    difficulty=card.get('difficulty', 'medium'),
                    user_id=current_user.id, material_id=material.id
                )
                db.session.add(new_card)
            db.session.commit()
            print(f"Generated {len(flashcards_data)} flashcards.")

        time.sleep(5)

        # 4. Quizzes
        print("Generating quizzes...")
        quiz_data = ai_service.generate_quizzes(text)
        if quiz_data:
            new_quiz = Quiz(material_id=material.id, questions=quiz_data)
            db.session.add(new_quiz)
            db.session.commit()
            print(f"Generated quiz with {len(quiz_data)} questions.")
        
        time.sleep(5)
        
        # 5. Exam Booster (Rapid Revision & Probable Questions)
        print("Generating Exam Booster...")
        booster_data = ai_service.generate_exam_booster(text)
        if booster_data:
            # Check if exists, update or create
            existing_booster = ExamBooster.query.filter_by(material_id=material.id).first()
            if existing_booster:
                existing_booster.revision_notes = booster_data.get('revision_notes', '')
                existing_booster.probable_questions = booster_data.get('probable_questions', [])
            else:
                new_booster = ExamBooster(
                    material_id=material.id,
                    revision_notes=booster_data.get('revision_notes', ''),
                    probable_questions=booster_data.get('probable_questions', [])
                )
                db.session.add(new_booster)
            db.session.commit()
            print(f"Exam Booster generated for material {id}.")

        print(f"Material {id} fully processed.")
        return jsonify({'status': 'completed'})
    except Exception as e:
        print(f"Critical error in process_material: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/materials', methods=['GET'])
@login_required
def get_materials():
    materials = StudyMaterial.query.filter_by(user_id=current_user.id).order_by(StudyMaterial.created_at.desc()).all()
    return jsonify([{
        'id': m.id,
        'filename': m.filename,
        'created_at': m.created_at.isoformat()
    } for m in materials])

@api_bp.route('/material/<int:id>', methods=['DELETE'])
@login_required
def delete_material(id):
    material = StudyMaterial.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    try:
        # 1. Delete associated data first
        Flashcard.query.filter_by(material_id=id).delete()
        
        # Delete quiz results by finding quiz IDs for this material
        quiz_ids = [q.id for q in Quiz.query.filter_by(material_id=id).all()]
        if quiz_ids:
            from models import QuizResult
            QuizResult.query.filter(QuizResult.quiz_id.in_(quiz_ids)).delete(synchronize_session=False)
            
        Quiz.query.filter_by(material_id=id).delete()
        ExamBooster.query.filter_by(material_id=id).delete()
        
        # 2. Remove the physical file
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], material.filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            
        # 3. Delete the material record
        db.session.delete(material)
        db.session.commit()
        
        return jsonify({'message': 'Material deleted successfully'})
    except Exception as e:
        db.session.rollback()
        print(f"Delete Error: {e}")
        return jsonify({'error': 'Failed to delete material'}), 500

@api_bp.route('/material/<int:id>', methods=['GET'])
@login_required
def get_material_detail(id):
    material = StudyMaterial.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    flashcards = Flashcard.query.filter_by(material_id=id).all()
    quizzes = Quiz.query.filter_by(material_id=id).all()
    
    return jsonify({
        'id': material.id,
        'filename': material.filename,
        'summary': material.summary,
        'learning_path': material.learning_path,
        'flashcards': [{
            'id': f.id,
            'question': f.question,
            'answer': f.answer,
            'difficulty': f.difficulty,
            'is_completed': f.is_completed
        } for f in flashcards],
        'quizzes': [{
            'id': q.id,
            'questions': q.questions
        } for q in quizzes]
    })

@api_bp.route('/flashcard/<int:id>/complete', methods=['POST'])
@login_required
def toggle_flashcard_completion(id):
    flashcard = Flashcard.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    flashcard.is_completed = not flashcard.is_completed
    db.session.commit()
    return jsonify({'status': 'success', 'is_completed': flashcard.is_completed})

@api_bp.route('/quiz/submit', methods=['POST'])
@login_required
def submit_quiz_result():
    data = request.json
    quiz_id = data.get('quiz_id')
    score = data.get('score')
    total = data.get('total')
    
    if quiz_id is None or score is None or total is None:
        return jsonify({'error': 'Missing data'}), 400
        
    result = QuizResult(
        user_id=current_user.id,
        quiz_id=quiz_id,
        score=score,
        total_questions=total
    )
    db.session.add(result)
    
    # Update user average score
    current_user.total_quizzes += 1
    # Simple calculation: (OldAvg * (Total-1) + NewScorePercentage) / Total
    new_score_pct = (score / total) * 100
    current_user.avg_score = ((current_user.avg_score * (current_user.total_quizzes - 1)) + new_score_pct) / current_user.total_quizzes
    
    db.session.commit()
    return jsonify({'status': 'success', 'avg_score': current_user.avg_score})

@api_bp.route('/stats/progress/<int:material_id>', methods=['GET'])
@login_required
def get_material_progress(material_id):
    total_cards = Flashcard.query.filter_by(material_id=material_id).count()
    completed_cards = Flashcard.query.filter_by(material_id=material_id, is_completed=True).count()
    
    progress = (completed_cards / total_cards * 100) if total_cards > 0 else 0
    return jsonify({'progress': round(progress, 1)})
