"""
SQLAlchemy models for Bass Practice application.
"""
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class UserProfile(db.Model):
    """User profile settings for the local user."""
    __tablename__ = 'user_profile'
    
    id = db.Column(db.Integer, primary_key=True)
    skill_level = db.Column(db.Integer, default=1)  # 1-10 scale
    skill_category = db.Column(db.String(20), default='beginner')  # beginner, intermediate, advanced
    preferred_genre = db.Column(db.String(50), default='rock')
    session_duration = db.Column(db.Integer, default=30)  # minutes
    bass_tuning = db.Column(db.String(20), default='standard')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserProfile {self.skill_category} level {self.skill_level}>'


class Exercise(db.Model):
    """Exercise definitions for practice sessions."""
    __tablename__ = 'exercises'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(30), nullable=False)  # scales, arpeggios, rhythm, technique, theory
    subcategory = db.Column(db.String(50))
    difficulty_level = db.Column(db.Integer, nullable=False)  # 1-10
    estimated_duration = db.Column(db.Integer, nullable=False)  # minutes
    instructions = db.Column(db.Text)
    tips = db.Column(db.Text)
    prerequisites = db.Column(db.Text)  # JSON array of exercise IDs
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    session_exercises = db.relationship('SessionExercise', backref='exercise', lazy=True)
    
    def __repr__(self):
        return f'<Exercise {self.title}>'


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


class DynamicExercise(db.Model):
    """Dynamically generated exercises based on music theory."""
    __tablename__ = 'dynamic_exercises'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # scales, arpeggios, rhythm, technique, theory
    subcategory = db.Column(db.String(50))
    difficulty_level = db.Column(db.Integer, default=1)
    estimated_duration = db.Column(db.Integer, default=5)  # minutes
    
    # Exercise content
    description = db.Column(db.Text)
    instructions = db.Column(db.Text)
    tips = db.Column(db.Text)
    
    # Music theory data
    key_signature = db.Column(db.String(10))
    tempo_bpm = db.Column(db.Integer)
    tab_notation = db.Column(db.Text)
    notes_data = db.Column(db.Text)  # JSON array of notes
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    session_exercises = db.relationship('SessionExercise', backref='dynamic_exercise', lazy=True)
    
    def __repr__(self):
        return f'<DynamicExercise {self.title}>'


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


class Song(db.Model):
    """Songs for practice tracking."""
    __tablename__ = 'songs'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100))
    genre = db.Column(db.String(50))
    difficulty_level = db.Column(db.Integer)  # 1-10
    key_signature = db.Column(db.String(10))
    tempo_bpm = db.Column(db.Integer)
    duration_minutes = db.Column(db.Integer)
    bass_notes = db.Column(db.Text)  # JSON array of bass notes/tabs
    chord_progression = db.Column(db.Text)  # JSON array of chords
    youtube_url = db.Column(db.String(255))
    practice_notes = db.Column(db.Text)
    mastery_level = db.Column(db.Integer, default=0)  # 0-5 scale
    last_practiced = db.Column(db.Date)
    practice_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Song {self.title} by {self.artist}>'


class ChordProgression(db.Model):
    """Common chord progressions with bass line examples."""
    __tablename__ = 'chord_progressions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # e.g., "I-IV-V"
    numerals = db.Column(db.String(50), nullable=False)  # e.g., "I-IV-V"
    progression = db.Column(db.Text, nullable=False)  # JSON array of chord symbols
    genre = db.Column(db.String(50))
    difficulty_level = db.Column(db.Integer)
    description = db.Column(db.Text)
    bass_line_examples = db.Column(db.Text)  # JSON array of example bass lines
    common_songs = db.Column(db.Text)  # Songs using this progression
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ChordProgression {self.name}>'


class EarTrainingExercise(db.Model):
    """Ear training exercise definitions."""
    __tablename__ = 'ear_training_exercises'
    
    id = db.Column(db.Integer, primary_key=True)
    exercise_type = db.Column(db.String(50), nullable=False)  # interval, chord, melody
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    difficulty_level = db.Column(db.Integer)
    root_note = db.Column(db.String(10))  # Base note for the exercise
    correct_answer = db.Column(db.Text)  # JSON array of correct answers
    options = db.Column(db.Text)  # JSON array of multiple choice options
    hints = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    results = db.relationship('EarTrainingResult', backref='exercise', lazy=True)
    
    def __repr__(self):
        return f'<EarTrainingExercise {self.title}>'


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


class PracticeStreak(db.Model):
    """Track daily practice streaks."""
    __tablename__ = 'practice_streaks'
    
    id = db.Column(db.Integer, primary_key=True)
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    last_practice_date = db.Column(db.Date)
    total_practice_days = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<PracticeStreak current={self.current_streak} longest={self.longest_streak}>'


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
