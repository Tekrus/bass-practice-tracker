from datetime import datetime
from ..base import db

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
    
    def get_recommended_difficulty(self, category=None):
        """Map absolute skill level (1-10) to recommended exercise difficulty (1-5)."""
        # Simple mapping: 1-2 -> 1, 3-4 -> 2, 5-6 -> 3, 7-8 -> 4, 9-10 -> 5
        return max(1, min(5, (self.skill_level + 1) // 2))
    
    def update_preferences(self, **kwargs):
        """Update user preferences from keyword arguments."""
        valid_fields = ['skill_level', 'skill_category', 'preferred_genre', 'session_duration', 'bass_tuning']
        for key, value in kwargs.items():
            if key in valid_fields:
                setattr(self, key, value)
        return self

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

__all__ = ['UserProfile', 'PracticeStreak']
