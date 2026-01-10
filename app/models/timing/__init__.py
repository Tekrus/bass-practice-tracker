from datetime import datetime, date
from ..base import db

class TimingSession(db.Model):
    """Timing practice session records."""
    __tablename__ = 'timing_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_date = db.Column(db.Date, nullable=False, default=date.today)
    tempo_bpm = db.Column(db.Integer, nullable=False)
    game_mode = db.Column(db.String(30), nullable=False)  # groove, precision, endurance, subdivisions
    difficulty = db.Column(db.Integer, default=1)  # 1-5
    total_notes = db.Column(db.Integer, default=0)
    perfect_hits = db.Column(db.Integer, default=0)  # Within tight threshold
    good_hits = db.Column(db.Integer, default=0)  # Within acceptable threshold
    early_hits = db.Column(db.Integer, default=0)
    late_hits = db.Column(db.Integer, default=0)
    missed_notes = db.Column(db.Integer, default=0)
    average_timing_ms = db.Column(db.Float, default=0.0)  # Average deviation from perfect
    score = db.Column(db.Integer, default=0)
    duration_seconds = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
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

class TimingHighScore(db.Model):
    """High scores for timing practice games."""
    __tablename__ = 'timing_high_scores'
    
    id = db.Column(db.Integer, primary_key=True)
    game_mode = db.Column(db.String(30), nullable=False)
    tempo_bpm = db.Column(db.Integer, nullable=False)
    difficulty = db.Column(db.Integer, default=1)
    high_score = db.Column(db.Integer, default=0)
    best_accuracy = db.Column(db.Float, default=0.0)  # Percentage
    best_streak = db.Column(db.Integer, default=0)  # Consecutive perfect hits
    achieved_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<TimingHighScore {self.game_mode} @ {self.tempo_bpm}bpm: {self.high_score}>'

__all__ = ['TimingSession', 'TimingHighScore']
