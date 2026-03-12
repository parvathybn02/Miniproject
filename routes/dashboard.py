from flask import Blueprint, render_template
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from extensions import db

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def index():
    # Update Streak Logic
    today = date.today()
    if not current_user.last_streak_update:
        current_user.study_streak = 1
        current_user.last_streak_update = datetime.utcnow()
    else:
        last_date = current_user.last_streak_update.date()
        if last_date == today - timedelta(days=1):
            # Perfect, increment streak
            current_user.study_streak += 1
            current_user.last_streak_update = datetime.utcnow()
        elif last_date < today - timedelta(days=1):
            # Missed a day, reset streak
            current_user.study_streak = 1
            current_user.last_streak_update = datetime.utcnow()
        # if last_date == today, do nothing (keep current streak)
        
    db.session.commit()
    return render_template('dashboard.html', user=current_user)

@dashboard_bp.route('/flashcards')
@login_required
def flashcards():
    return render_template('flashcards.html')

@dashboard_bp.route('/quizzes')
@login_required
def quizzes():
    return render_template('quizzes.html')

@dashboard_bp.route('/study-rooms')
@login_required
def study_rooms():
    return render_template('study_rooms.html')

@dashboard_bp.route('/learning-path/<int:material_id>')
@login_required
def learning_path(material_id):
    return render_template('learning_path.html', material_id=material_id)

@dashboard_bp.route('/material/<int:material_id>')
@login_required
def material_detail(material_id):
    return render_template('material_detail.html', material_id=material_id)
