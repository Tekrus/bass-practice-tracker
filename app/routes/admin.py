from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import date, timedelta
from ..models import db, UserProfile, Exercise, ChordProgression, PracticeSession, Progress, Song

bp = Blueprint('admin', __name__)

@bp.route('/settings', methods=['GET', 'POST'])
def settings():
    """User settings page."""
    profile = UserProfile.query.first()
    
    if request.method == 'POST':
        if not profile:
            profile = UserProfile()
            db.session.add(profile)
        
        profile.skill_level = request.form.get('skill_level', type=int) or 1
        profile.skill_category = request.form.get('skill_category', 'beginner')
        profile.preferred_genre = request.form.get('preferred_genre', 'rock')
        profile.session_duration = request.form.get('session_duration', type=int) or 30
        profile.bass_tuning = request.form.get('bass_tuning', 'standard')
        
        db.session.commit()
        flash('Settings saved!', 'success')
        # Here we use dashboard.dashboard as it's the new blueprint name
        return redirect(url_for('dashboard.dashboard'))
    
    return render_template('settings.html', profile=profile)


@bp.route('/admin/reseed', methods=['POST'])
def reseed_database():
    """Force reseed the database with initial data."""
    from ..seed_data import seed_exercises, seed_chord_progressions, seed_progress
    
    # Clear existing data
    Exercise.query.delete()
    ChordProgression.query.delete()
    
    # Reseed
    seed_exercises()
    seed_chord_progressions()
    seed_progress()
    
    db.session.commit()
    
    flash(f'Database reseeded! {Exercise.query.count()} exercises added.', 'success')
    return redirect(url_for('dashboard.dashboard'))


@bp.route('/admin/status')
def database_status():
    """Check database status."""
    status = {
        'exercises': Exercise.query.count(),
        'exercises_by_category': {},
        'chord_progressions': ChordProgression.query.count(),
        'ear_training_exercises': 'Dynamic (not stored in DB)',
        'practice_sessions': PracticeSession.query.count(),
        'songs': Song.query.count(),
        'user_profile': UserProfile.query.first() is not None
    }
    
    # Get exercise count by category
    categories = db.session.query(Exercise.category, db.func.count(Exercise.id)).group_by(Exercise.category).all()
    status['exercises_by_category'] = {cat: count for cat, count in categories}
    
    return jsonify(status)


@bp.route('/api/progress-data')
def api_progress_data():
    """Get progress data for charts."""
    thirty_days_ago = date.today() - timedelta(days=30)
    
    sessions = PracticeSession.query.filter(
        PracticeSession.session_date >= thirty_days_ago,
        PracticeSession.is_completed == True
    ).all()
    
    daily_data = {}
    for session in sessions:
        date_str = session.session_date.isoformat()
        daily_data[date_str] = daily_data.get(date_str, 0) + (session.actual_duration or 0)
    
    categories = Progress.query.all()
    category_data = {p.category: p.skill_level for p in categories}
    
    return jsonify({
        'daily_practice': daily_data,
        'category_progress': category_data
    })
