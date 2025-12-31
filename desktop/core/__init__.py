# Core module for bass practice desktop app
from .database import Database, get_db
from .models import (
    UserProfile, Exercise, DynamicExercise, PracticeSession, SessionExercise,
    Progress, Song, ChordProgression, EarTrainingExercise, EarTrainingResult,
    PracticeStreak, QuizResult, TimingSession, TimingHighScore
)

__all__ = [
    'Database', 'get_db',
    'UserProfile', 'Exercise', 'DynamicExercise', 'PracticeSession', 'SessionExercise',
    'Progress', 'Song', 'ChordProgression', 'EarTrainingExercise', 'EarTrainingResult',
    'PracticeStreak', 'QuizResult', 'TimingSession', 'TimingHighScore'
]
