"""
Song practice management logic.
"""
import random
from datetime import date, timedelta
from .models import db, Song


def get_recently_practiced_songs(days=7):
    """Get songs practiced in the last N days."""
    cutoff_date = date.today() - timedelta(days=days)
    return Song.query.filter(Song.last_practiced >= cutoff_date).all()


def generate_daily_song_playlist(max_songs=5):
    """
    Generate a playlist of songs to practice based on user's song library
    and practice patterns.
    """
    all_songs = Song.query.all()
    
    if not all_songs:
        return []
    
    # Categorize songs by mastery level
    new_songs = [s for s in all_songs if s.mastery_level <= 1]
    learning_songs = [s for s in all_songs if 2 <= s.mastery_level <= 3]
    review_songs = [s for s in all_songs if s.mastery_level >= 4]
    
    playlist = []
    
    # Priority 1: Songs that haven't been practiced recently
    recently_practiced = get_recently_practiced_songs(days=7)
    recently_practiced_ids = {s.id for s in recently_practiced}
    overdue_songs = [s for s in all_songs if s.id not in recently_practiced_ids]
    
    # Priority 2: New songs (introduce 1-2 new songs)
    available_new = [s for s in new_songs if s.id not in recently_practiced_ids]
    if available_new:
        count = min(2, len(available_new))
        playlist.extend(random.sample(available_new, count))
    
    # Priority 3: Songs currently being learned
    available_learning = [s for s in learning_songs if s not in playlist]
    if available_learning and len(playlist) < max_songs:
        remaining = max_songs - len(playlist)
        count = min(remaining, min(3, len(available_learning)))
        playlist.extend(random.sample(available_learning, count))
    
    # Priority 4: Overdue songs for review
    available_overdue = [s for s in overdue_songs if s not in playlist]
    if available_overdue and len(playlist) < max_songs:
        remaining = max_songs - len(playlist)
        count = min(remaining, len(available_overdue))
        playlist.extend(random.sample(available_overdue, count))
    
    # Priority 5: Mastered songs for maintenance
    available_review = [s for s in review_songs if s not in playlist]
    if available_review and len(playlist) < max_songs:
        remaining = max_songs - len(playlist)
        count = min(remaining, len(available_review))
        playlist.extend(random.sample(available_review, count))
    
    return playlist


def update_song_mastery(song, practice_quality):
    """
    Update song mastery level based on practice performance.
    
    Args:
        song: Song model instance
        practice_quality: 1-5 rating of practice quality
    """
    # Update practice count
    song.practice_count += 1
    song.last_practiced = date.today()
    
    # Adjust mastery based on practice quality
    if practice_quality >= 4:  # Good/Excellent practice
        song.mastery_level = min(5, song.mastery_level + 1)
    elif practice_quality <= 2:  # Poor practice
        song.mastery_level = max(0, song.mastery_level - 1)
    # Quality of 3 maintains current level
    
    db.session.commit()
    
    return song
