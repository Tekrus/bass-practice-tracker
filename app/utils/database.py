from datetime import date, timedelta
from ..models import db, Progress, PracticeStreak, PracticeSession

def calculate_progress_accuracy(category):
    """
    Calculate the accuracy/completion rate for a given practice category.
    This is a helper for dashboard visualizations.
    """
    progress = Progress.query.filter_by(category=category).first()
    if not progress:
        return 0.0
    
    # Simple metric: ratio of exercises completed vs a target (e.g., 100 for mastery)
    mastery_target = 100
    return min(100.0, (progress.exercises_completed / mastery_target) * 100.0)

def get_user_streak():
    """
    Get the current practice streak for the user.
    """
    streak = PracticeStreak.query.first()
    if not streak:
        return 0
    
    # Verify if streak is still active (practiced today or yesterday)
    today = date.today()
    if streak.last_practice_date:
        days_since = (today - streak.last_practice_date).days
        if days_since > 1:
            # Streak expired
            return 0
    
    return streak.current_streak

def update_progress_for_category(category, duration_minutes=0):
    """
    Update progress for a given category when an exercise is completed.
    Calculates skill_level based on exercises completed.
    """
    # Get or create progress entry for this category
    progress = Progress.query.filter_by(category=category).first()
    if not progress:
        progress = Progress(category=category)
        db.session.add(progress)
    
    # Update exercise count and practice time
    progress.exercises_completed += 1
    progress.last_practiced = date.today()
    if duration_minutes:
        progress.total_practice_time += duration_minutes
    
    # Calculate skill_level based on exercises completed
    # Formula: skill_level = 1 - (1 / (1 + exercises / 10))
    exercises = progress.exercises_completed
    if exercises <= 0:
        progress.skill_level = 0.0
    else:
        progress.skill_level = min(1.0, 1.0 - (1.0 / (1.0 + exercises / 10.0)))
    
    db.session.commit()
    return progress
