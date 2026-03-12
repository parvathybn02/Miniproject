from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from extensions import db
from models import StudyMaterial, ExamBooster
from services.ai_service import AIService
import time

booster_bp = Blueprint('booster', __name__)
ai_service = AIService()

@booster_bp.route('/exam-booster')
@booster_bp.route('/exam-booster/<int:material_id>')
@login_required
def view_booster(material_id=None):
    material = None
    booster = None
    mode = request.args.get('mode', 'both') # revision, questions, or both
    if material_id:
        material = StudyMaterial.query.filter_by(id=material_id, user_id=current_user.id).first_or_404()
        booster = ExamBooster.query.filter_by(material_id=material_id).first()
    return render_template('exam_booster.html', material=material, booster=booster, material_id=material_id, mode=mode)

@booster_bp.route('/api/booster/generate/<int:material_id>', methods=['POST'])
@login_required
def generate_booster(material_id):
    material = StudyMaterial.query.get_or_404(material_id)
    if material.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Check if exists
    existing = ExamBooster.query.filter_by(material_id=material_id).first()
    if existing:
        return jsonify({'status': 'exists'})

    print(f"Generating Exam Booster for material {material_id}...")
    text = material.content_text[:15000] if material.content_text else ""
    if not text:
        return jsonify({'error': 'No content found in material'}), 400

    try:
        data = ai_service.generate_exam_booster(text)
        if data:
            new_booster = ExamBooster(
                material_id=material_id,
                revision_notes=data.get('revision_notes', ''),
                probable_questions=data.get('probable_questions', [])
            )
            db.session.add(new_booster)
            db.session.commit()
            return jsonify({'status': 'completed'})
        else:
            return jsonify({'error': 'AI failed to generate content'}), 500
    except Exception as e:
        print(f"Error in generate_booster: {e}")
        return jsonify({'error': str(e)}), 500

@booster_bp.route('/api/booster/<int:material_id>')
@login_required
def get_booster(material_id):
    booster = ExamBooster.query.filter_by(material_id=material_id).first_or_404()
    return jsonify({
        'revision_notes': booster.revision_notes,
        'probable_questions': booster.probable_questions
    })
