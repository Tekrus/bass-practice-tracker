from datetime import datetime
from ..base import db

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

__all__ = ['Exercise', 'Song', 'ChordProgression', 'EarTrainingExercise', 'DynamicExercise']
