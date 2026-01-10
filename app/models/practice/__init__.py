from datetime import datetime, date
from ..base import db

class PracticeSession(db.Model):
    """Practice session records."""
    __tablename__ = 'practice_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_date = db.Column(db.Date, nullable=False, default=date.today)
    planned_duration = db.Column(db.Integer)  # minutes
    actual_duration = db.Column(db.Integer)  # minutes
    completed_exercises = db.Column(db.Integer, default=0)
    total_exercises = db.Column(db.Integer, default=0)
    session_notes = db.Column(db.Text)
    session_rating = db.Column(db.Integer)  # 1-5 stars
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    exercises = db.relationship('SessionExercise', backref='session', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<PracticeSession {self.session_date}>'
    
    def calculate_accuracy(self):
        """Calculate the percentage of completed exercises in this session."""
        if self.total_exercises == 0:
            return 0.0
        return (self.completed_exercises / self.total_exercises) * 100.0
    
    def get_duration(self):
        """Get the duration of the session in minutes."""
        return self.actual_duration or self.planned_duration or 0

class SessionExercise(db.Model):
    """Junction table for exercises within a practice session."""
    __tablename__ = 'session_exercises'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('practice_sessions.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=True)  # For static exercises
    dynamic_exercise_id = db.Column(db.Integer, db.ForeignKey('dynamic_exercises.id'), nullable=True)  # For dynamic
    order_index = db.Column(db.Integer, default=0)
    phase = db.Column(db.String(20))  # warmup, technique, musical, cooldown
    completed = db.Column(db.Boolean, default=False)
    planned_duration = db.Column(db.Integer)  # minutes
    actual_duration = db.Column(db.Integer)  # minutes
    difficulty_felt = db.Column(db.Integer)  # 1-10
    exercise_notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<SessionExercise in session {self.session_id}>'
    
    @property
    def exercise_title(self):
        """Get the exercise title from either static or dynamic exercise."""
        if self.dynamic_exercise:
            return self.dynamic_exercise.title
        elif self.exercise:
            return self.exercise.title
        return "Unknown Exercise"
    
    @property
    def exercise_data(self):
        """Get exercise data from either source."""
        if self.dynamic_exercise:
            return self.dynamic_exercise
        return self.exercise

class Progress(db.Model):
    """Track progress in each exercise category."""
    __tablename__ = 'progress'
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(30), nullable=False)  # scales, arpeggios, etc.
    skill_level = db.Column(db.Float, default=0.0)  # 0.0-1.0 progress within level
    exercises_completed = db.Column(db.Integer, default=0)
    total_practice_time = db.Column(db.Integer, default=0)  # minutes
    last_practiced = db.Column(db.Date)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Progress {self.category}: {self.skill_level}>'
    
    def update_skill_level(self):
        """Update skill level based on completed exercises using logarithmic curve."""
        if self.exercises_completed <= 0:
            self.skill_level = 0.0
        else:
            # Formula: skill_level = 1 - (1 / (1 + exercises / 10))
            self.skill_level = min(1.0, 1.0 - (1.0 / (1.0 + self.exercises_completed / 10.0)))
        return self.skill_level
    
    def get_completion_percentage(self, target=100):
        """Calculate completion percentage toward a mastery target."""
        if target <= 0:
            return 100.0
        return min(100.0, (self.exercises_completed / target) * 100.0)

__all__ = ['PracticeSession', 'SessionExercise', 'Progress']
