from flask import Blueprint, render_template, redirect, url_for
from datetime import date
from ..models import db, UserProfile, PracticeStreak, PracticeSession, Progress
from ..song_manager import generate_daily_song_playlist
from ..exercise_generator import EXERCISE_CATEGORIES
from ..config.settings import RECENT_SESSIONS_COUNT
from ..utils.database import get_user_streak

bp = Blueprint('dashboard', __name__)

@bp.route('/')
def dashboard():
    """Main dashboard showing practice overview."""
    # Get user profile
    profile = UserProfile.query.first()
    if not profile:
        return redirect(url_for('admin.settings'))
    
    # Get practice streak
    streak = PracticeStreak.query.first()
    if not streak:
        streak = PracticeStreak()
        db.session.add(streak)
        db.session.commit()
    
    # Get today's practice session if exists
    today = date.today()
    todays_session = PracticeSession.query.filter_by(session_date=today).first()
    
    # Get recent practice sessions
    recent_sessions = PracticeSession.query.order_by(
        PracticeSession.session_date.desc()
    ).limit(RECENT_SESSIONS_COUNT).all()
    
    # Get progress by category
    progress_data = Progress.query.all()
    
    # Get daily song playlist
    song_playlist = generate_daily_song_playlist()
    
    # Calculate stats
    total_practice_time = db.session.query(
        db.func.sum(PracticeSession.actual_duration)
    ).scalar() or 0
    
    total_sessions = PracticeSession.query.filter_by(is_completed=True).count()
    
    # Find the lowest skill category for recommended exercise
    lowest_category = None
    if progress_data:
        lowest_progress = min(progress_data, key=lambda p: p.skill_level)
        lowest_category = lowest_progress.category
    else:
        # If no progress yet, default to first category
        lowest_category = EXERCISE_CATEGORIES[0] if EXERCISE_CATEGORIES else 'scales'
    
    return render_template('dashboard.html',
        profile=profile,
        streak=streak,
        todays_session=todays_session,
        recent_sessions=recent_sessions,
        progress_data=progress_data,
        song_playlist=song_playlist,
        total_practice_time=total_practice_time,
        total_sessions=total_sessions,
        recommended_category=lowest_category
    )

@bp.route('/progress')
def progress():
    """View detailed progress statistics."""
    from ..models import EarTrainingResult, Song
    from datetime import timedelta
    
    # Get progress by category
    progress_data = Progress.query.all()
    
    # Get practice history
    sessions = PracticeSession.query.filter_by(is_completed=True).order_by(
        PracticeSession.session_date.desc()
    ).limit(30).all()
    
    # Get streak info
    streak = PracticeStreak.query.first()
    
    # Calculate weekly practice time
    week_ago = date.today() - timedelta(days=7)
    weekly_time = db.session.query(
        db.func.sum(PracticeSession.actual_duration)
    ).filter(
        PracticeSession.session_date >= week_ago,
        PracticeSession.is_completed == True
    ).scalar() or 0
    
    # Get ear training stats (for dynamic exercises only, exercise_id=0)
    total_ear = EarTrainingResult.query.filter_by(exercise_id=0).count()
    correct_ear = EarTrainingResult.query.filter_by(exercise_id=0, correct=True).count()
    ear_stats = {
        'overall': {
            'total': total_ear,
            'correct': correct_ear,
            'accuracy': (correct_ear / total_ear * 100) if total_ear > 0 else 0
        }
    }
    
    # Get song progress
    total_songs = Song.query.count()
    mastered_songs = Song.query.filter(Song.mastery_level >= 4).count()
    
    # Find the lowest skill category for recommended exercise
    lowest_category = None
    if progress_data:
        lowest_progress = min(progress_data, key=lambda p: p.skill_level)
        lowest_category = lowest_progress.category
    else:
        # If no progress yet, default to first category
        lowest_category = EXERCISE_CATEGORIES[0] if EXERCISE_CATEGORIES else 'scales'
    
    return render_template('progress.html',
        progress_data=progress_data,
        sessions=sessions,
        streak=streak,
        weekly_time=weekly_time,
        ear_stats=ear_stats,
        total_songs=total_songs,
        mastered_songs=mastered_songs,
        recommended_category=lowest_category
    )
