from ..models import db, Exercise, Progress, PracticeStreak
from .exercises import seed_exercises
from .chord_progressions import seed_chord_progressions

def seed_database():
    """Seed the database with initial data if empty."""
    # Check if already seeded
    if Exercise.query.first():
        return
    
    # Seed exercises
    seed_exercises()
    
    # Seed chord progressions
    seed_chord_progressions()
    
    # Initialize progress tracking for each category
    seed_progress()
    
    # Initialize practice streak
    if not PracticeStreak.query.first():
        streak = PracticeStreak()
        db.session.add(streak)
    
    db.session.commit()

def seed_progress():
    """Initialize progress tracking for each category."""
    categories = ['scales', 'arpeggios', 'rhythm', 'technique', 'theory']
    
    for category in categories:
        if not Progress.query.filter_by(category=category).first():
            progress = Progress(category=category)
            db.session.add(progress)
    
    db.session.commit()
