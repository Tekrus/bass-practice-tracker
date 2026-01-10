from datetime import datetime
from .base import db
from .practice import PracticeSession, SessionExercise, Progress
from .content import Exercise, Song, ChordProgression, EarTrainingExercise, DynamicExercise
from .user import UserProfile, PracticeStreak
from .timing import TimingSession, TimingHighScore

class EarTrainingResult(db.Model):
    """Results from ear training exercises."""
    __tablename__ = 'ear_training_results'
    
    id = db.Column(db.Integer, primary_key=True)
    exercise_id = db.Column(db.Integer, db.ForeignKey('ear_training_exercises.id'), nullable=False)
    user_answer = db.Column(db.Text)
    correct = db.Column(db.Boolean)
    response_time_ms = db.Column(db.Integer)
    practiced_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<EarTrainingResult exercise={self.exercise_id} correct={self.correct}>'

class QuizResult(db.Model):
    """Results from dynamically generated quiz attempts."""
    __tablename__ = 'quiz_results'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, default=0)  # Not used for dynamic quizzes
    quiz_type = db.Column(db.String(50), nullable=False)  # Category: fretboard, theory, chords, scales, rhythm, technique
    user_answer = db.Column(db.String(100))
    correct = db.Column(db.Boolean)
    response_time_ms = db.Column(db.Integer)
    attempted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<QuizResult type={self.quiz_type} correct={self.correct}>'

__all__ = [
    'db', 
    'UserProfile', 'PracticeStreak',
    'Exercise', 'Song', 'ChordProgression', 'EarTrainingExercise', 'DynamicExercise',
    'PracticeSession', 'SessionExercise', 'Progress',
    'TimingSession', 'TimingHighScore',
    'EarTrainingResult', 'QuizResult'
]
