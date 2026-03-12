from extensions import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Progress tracking
    study_streak = db.Column(db.Integer, default=0)
    total_quizzes = db.Column(db.Integer, default=0)
    avg_score = db.Column(db.Float, default=0.0)
    last_login = db.Column(db.DateTime)
    last_streak_update = db.Column(db.DateTime)
    
    materials = db.relationship('StudyMaterial', backref='owner', lazy=True)
    flashcards = db.relationship('Flashcard', backref='user', lazy=True)
    quiz_results = db.relationship('QuizResult', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class StudyMaterial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    content_text = db.Column(db.Text)
    summary = db.Column(db.Text)
    learning_path = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    flashcards = db.relationship('Flashcard', backref='material', lazy=True)
    quizzes = db.relationship('Quiz', backref='material', lazy=True)

class Flashcard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('study_material.id'), nullable=False)
    last_reviewed = db.Column(db.DateTime)
    next_review = db.Column(db.DateTime, default=datetime.utcnow)
    interval = db.Column(db.Integer, default=1) # Days for spaced repetition
    difficulty = db.Column(db.String(20), default='medium') # easy, medium, hard
    is_completed = db.Column(db.Boolean, default=False)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('study_material.id'), nullable=False)
    questions = db.Column(db.JSON) # List of {question, options, correct, explanation}
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class QuizResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

class StudyRoom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    messages = db.relationship('Message', backref='room', lazy=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('study_room.id'), nullable=False)
    username = db.Column(db.String(80)) # Cache username for efficiency

class ExamBooster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('study_material.id'), nullable=False)
    revision_notes = db.Column(db.Text) # Bullet points for quick revision
    probable_questions = db.Column(db.JSON) # List of {question, topic, importance}
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    material = db.relationship('StudyMaterial', backref=db.backref('exam_booster', uselist=False))
