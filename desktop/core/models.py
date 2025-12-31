"""
SQLAlchemy models for Bass Practice desktop application.
Standalone models without Flask-SQLAlchemy dependency.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class UserProfile(Base):
    """User profile settings for the local user."""
    __tablename__ = 'user_profile'
    
    id = Column(Integer, primary_key=True)
    skill_level = Column(Integer, default=1)  # 1-10 scale
    skill_category = Column(String(20), default='beginner')  # beginner, intermediate, advanced
    preferred_genre = Column(String(50), default='rock')
    session_duration = Column(Integer, default=30)  # minutes
    bass_tuning = Column(String(20), default='standard')
    
    # Audio settings
    input_device_id = Column(Integer, nullable=True)
    output_device_id = Column(Integer, nullable=True)
    buffer_size = Column(Integer, default=256)
    sample_rate = Column(Integer, default=48000)
    latency_offset_ms = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserProfile {self.skill_category} level {self.skill_level}>'


class Exercise(Base):
    """Exercise definitions for practice sessions."""
    __tablename__ = 'exercises'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    category = Column(String(30), nullable=False)  # scales, arpeggios, rhythm, technique, theory
    subcategory = Column(String(50))
    difficulty_level = Column(Integer, nullable=False)  # 1-10
    estimated_duration = Column(Integer, nullable=False)  # minutes
    instructions = Column(Text)
    tips = Column(Text)
    prerequisites = Column(Text)  # JSON array of exercise IDs
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session_exercises = relationship('SessionExercise', back_populates='exercise', lazy=True)
    
    def __repr__(self):
        return f'<Exercise {self.title}>'


class DynamicExercise(Base):
    """Dynamically generated exercises based on music theory."""
    __tablename__ = 'dynamic_exercises'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)  # scales, arpeggios, rhythm, technique, theory
    subcategory = Column(String(50))
    difficulty_level = Column(Integer, default=1)
    estimated_duration = Column(Integer, default=5)  # minutes
    
    # Exercise content
    description = Column(Text)
    instructions = Column(Text)
    tips = Column(Text)
    
    # Music theory data
    key_signature = Column(String(10))
    tempo_bpm = Column(Integer)
    tab_notation = Column(Text)
    notes_data = Column(Text)  # JSON array of notes
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session_exercises = relationship('SessionExercise', back_populates='dynamic_exercise', lazy=True)
    
    def __repr__(self):
        return f'<DynamicExercise {self.title}>'


class PracticeSession(Base):
    """Practice session records."""
    __tablename__ = 'practice_sessions'
    
    id = Column(Integer, primary_key=True)
    session_date = Column(Date, nullable=False, default=date.today)
    planned_duration = Column(Integer)  # minutes
    actual_duration = Column(Integer)  # minutes
    completed_exercises = Column(Integer, default=0)
    total_exercises = Column(Integer, default=0)
    session_notes = Column(Text)
    session_rating = Column(Integer)  # 1-5 stars
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    exercises = relationship('SessionExercise', back_populates='session', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<PracticeSession {self.session_date}>'


class SessionExercise(Base):
    """Junction table for exercises within a practice session."""
    __tablename__ = 'session_exercises'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('practice_sessions.id'), nullable=False)
    exercise_id = Column(Integer, ForeignKey('exercises.id'), nullable=True)  # For static exercises
    dynamic_exercise_id = Column(Integer, ForeignKey('dynamic_exercises.id'), nullable=True)  # For dynamic
    order_index = Column(Integer, default=0)
    phase = Column(String(20))  # warmup, technique, musical, cooldown
    completed = Column(Boolean, default=False)
    planned_duration = Column(Integer)  # minutes
    actual_duration = Column(Integer)  # minutes
    difficulty_felt = Column(Integer)  # 1-10
    exercise_notes = Column(Text)
    
    # Relationships
    session = relationship('PracticeSession', back_populates='exercises')
    exercise = relationship('Exercise', back_populates='session_exercises')
    dynamic_exercise = relationship('DynamicExercise', back_populates='session_exercises')
    
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


class Progress(Base):
    """Track progress in each exercise category."""
    __tablename__ = 'progress'
    
    id = Column(Integer, primary_key=True)
    category = Column(String(30), nullable=False)  # scales, arpeggios, etc.
    skill_level = Column(Float, default=0.0)  # 0.0-1.0 progress within level
    exercises_completed = Column(Integer, default=0)
    total_practice_time = Column(Integer, default=0)  # minutes
    last_practiced = Column(Date)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Progress {self.category}: {self.skill_level}>'


class Song(Base):
    """Songs for practice tracking."""
    __tablename__ = 'songs'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    artist = Column(String(100))
    genre = Column(String(50))
    difficulty_level = Column(Integer)  # 1-10
    key_signature = Column(String(10))
    tempo_bpm = Column(Integer)
    duration_minutes = Column(Integer)
    bass_notes = Column(Text)  # JSON array of bass notes/tabs
    chord_progression = Column(Text)  # JSON array of chords
    youtube_url = Column(String(255))
    practice_notes = Column(Text)
    mastery_level = Column(Integer, default=0)  # 0-5 scale
    last_practiced = Column(Date)
    practice_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Song {self.title} by {self.artist}>'


class ChordProgression(Base):
    """Common chord progressions with bass line examples."""
    __tablename__ = 'chord_progressions'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)  # e.g., "I-IV-V"
    numerals = Column(String(50), nullable=False)  # e.g., "I-IV-V"
    progression = Column(Text, nullable=False)  # JSON array of chord symbols
    genre = Column(String(50))
    difficulty_level = Column(Integer)
    description = Column(Text)
    bass_line_examples = Column(Text)  # JSON array of example bass lines
    common_songs = Column(Text)  # Songs using this progression
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ChordProgression {self.name}>'


class EarTrainingExercise(Base):
    """Ear training exercise definitions."""
    __tablename__ = 'ear_training_exercises'
    
    id = Column(Integer, primary_key=True)
    exercise_type = Column(String(50), nullable=False)  # interval, chord, melody
    title = Column(String(100), nullable=False)
    description = Column(Text)
    difficulty_level = Column(Integer)
    root_note = Column(String(10))  # Base note for the exercise
    correct_answer = Column(Text)  # JSON array of correct answers
    options = Column(Text)  # JSON array of multiple choice options
    hints = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    results = relationship('EarTrainingResult', back_populates='exercise', lazy=True)
    
    def __repr__(self):
        return f'<EarTrainingExercise {self.title}>'


class EarTrainingResult(Base):
    """Results from ear training exercises."""
    __tablename__ = 'ear_training_results'
    
    id = Column(Integer, primary_key=True)
    exercise_id = Column(Integer, ForeignKey('ear_training_exercises.id'), nullable=False)
    user_answer = Column(Text)
    correct = Column(Boolean)
    response_time_ms = Column(Integer)
    practiced_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    exercise = relationship('EarTrainingExercise', back_populates='results')
    
    def __repr__(self):
        return f'<EarTrainingResult exercise={self.exercise_id} correct={self.correct}>'


class PracticeStreak(Base):
    """Track daily practice streaks."""
    __tablename__ = 'practice_streaks'
    
    id = Column(Integer, primary_key=True)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_practice_date = Column(Date)
    total_practice_days = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<PracticeStreak current={self.current_streak} longest={self.longest_streak}>'


class QuizResult(Base):
    """Results from dynamically generated quiz attempts."""
    __tablename__ = 'quiz_results'
    
    id = Column(Integer, primary_key=True)
    quiz_id = Column(Integer, default=0)  # Not used for dynamic quizzes
    quiz_type = Column(String(50), nullable=False)  # Category: fretboard, theory, chords, scales, rhythm, technique
    user_answer = Column(String(100))
    correct = Column(Boolean)
    response_time_ms = Column(Integer)
    attempted_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<QuizResult type={self.quiz_type} correct={self.correct}>'


class TimingSession(Base):
    """Timing practice session records."""
    __tablename__ = 'timing_sessions'
    
    id = Column(Integer, primary_key=True)
    session_date = Column(Date, nullable=False, default=date.today)
    tempo_bpm = Column(Integer, nullable=False)
    game_mode = Column(String(30), nullable=False)  # groove, precision, endurance, subdivisions
    difficulty = Column(Integer, default=1)  # 1-5
    total_notes = Column(Integer, default=0)
    perfect_hits = Column(Integer, default=0)  # Within tight threshold
    good_hits = Column(Integer, default=0)  # Within acceptable threshold
    early_hits = Column(Integer, default=0)
    late_hits = Column(Integer, default=0)
    missed_notes = Column(Integer, default=0)
    average_timing_ms = Column(Float, default=0.0)  # Average deviation from perfect
    score = Column(Integer, default=0)
    duration_seconds = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<TimingSession {self.game_mode} @ {self.tempo_bpm}bpm score={self.score}>'
    
    @property
    def accuracy_percentage(self):
        """Calculate accuracy as percentage of perfect + good hits."""
        if self.total_notes == 0:
            return 0
        return round((self.perfect_hits + self.good_hits) / self.total_notes * 100, 1)
    
    @property
    def perfect_percentage(self):
        """Calculate percentage of perfect hits."""
        if self.total_notes == 0:
            return 0
        return round(self.perfect_hits / self.total_notes * 100, 1)


class TimingHighScore(Base):
    """High scores for timing practice games."""
    __tablename__ = 'timing_high_scores'
    
    id = Column(Integer, primary_key=True)
    game_mode = Column(String(30), nullable=False)
    tempo_bpm = Column(Integer, nullable=False)
    difficulty = Column(Integer, default=1)
    high_score = Column(Integer, default=0)
    best_accuracy = Column(Float, default=0.0)  # Percentage
    best_streak = Column(Integer, default=0)  # Consecutive perfect hits
    achieved_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<TimingHighScore {self.game_mode} @ {self.tempo_bpm}bpm: {self.high_score}>'
