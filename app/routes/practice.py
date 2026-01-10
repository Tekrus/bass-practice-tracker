from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import date
from ..models import db, UserProfile, Exercise, PracticeSession, SessionExercise
from ..practice_generator import generate_practice_session
from ..utils.database import update_progress_for_category

bp = Blueprint('practice', __name__)

@bp.route('/practice/generate', methods=['POST'])
def generate_practice():
    """Generate a new practice session."""
    profile = UserProfile.query.first()
    if not profile:
        flash('Please set up your profile first.', 'warning')
        return redirect(url_for('admin.settings'))
    
    # Check if we have exercises in the database
    exercise_count = Exercise.query.count()
    if exercise_count == 0:
        # Force reseed
        from ..seed_data import seed_database
        seed_database()
        flash('Exercise database has been initialized.', 'info')
    
    # Check if there's already a session for today
    today = date.today()
    existing_session = PracticeSession.query.filter_by(session_date=today).first()
    
    if existing_session and not existing_session.is_completed:
        return redirect(url_for('practice.practice_session', session_id=existing_session.id))
    
    # Generate new session
    session = generate_practice_session(
        skill_level=profile.skill_level,
        duration_minutes=profile.session_duration,
        preferred_genre=profile.preferred_genre
    )
    
    if session.total_exercises == 0:
        flash('Could not generate exercises. Please check the exercise library.', 'warning')
        return redirect(url_for('dashboard.dashboard'))
    
    return redirect(url_for('practice.practice_session', session_id=session.id))


@bp.route('/practice/<int:session_id>')
def practice_session(session_id):
    """View and interact with a practice session."""
    session = PracticeSession.query.get_or_404(session_id)
    profile = UserProfile.query.first()
    
    # Get session exercises with exercise details
    session_exercises = SessionExercise.query.filter_by(
        session_id=session_id
    ).order_by(SessionExercise.order_index).all()
    
    return render_template('practice.html',
        session=session,
        session_exercises=session_exercises,
        profile=profile
    )


@bp.route('/practice/<int:session_id>/exercise/<int:exercise_index>/complete', methods=['POST'])
def complete_exercise(session_id, exercise_index):
    """Mark an exercise as complete."""
    session_exercise = SessionExercise.query.filter_by(
        session_id=session_id,
        order_index=exercise_index
    ).first_or_404()
    
    session_exercise.completed = True
    session_exercise.actual_duration = request.form.get('actual_duration', type=int)
    session_exercise.difficulty_felt = request.form.get('difficulty_felt', type=int)
    session_exercise.exercise_notes = request.form.get('notes', '')
    
    # Update session completed count
    session = PracticeSession.query.get(session_id)
    session.completed_exercises = SessionExercise.query.filter_by(
        session_id=session_id, completed=True
    ).count()
    
    # Update progress for this category
    exercise_data = session_exercise.exercise_data
    if exercise_data:
        duration = session_exercise.actual_duration or 0
        update_progress_for_category(exercise_data.category, duration)
    
    db.session.commit()
    
    return jsonify({'success': True, 'completed': session.completed_exercises})


@bp.route('/practice/<int:session_id>/complete', methods=['POST'])
def complete_session(session_id):
    """Complete the entire practice session."""
    from ..models import PracticeStreak
    session = PracticeSession.query.get_or_404(session_id)
    
    session.is_completed = True
    session.actual_duration = request.form.get('actual_duration', type=int)
    session.session_rating = request.form.get('rating', type=int)
    session.session_notes = request.form.get('notes', '')
    
    # Update practice streak
    streak = PracticeStreak.query.first()
    today = date.today()
    
    if streak.last_practice_date:
        days_since = (today - streak.last_practice_date).days
        if days_since == 1:
            streak.current_streak += 1
        elif days_since > 1:
            streak.current_streak = 1
    else:
        streak.current_streak = 1
    
    streak.last_practice_date = today
    streak.total_practice_days += 1
    if streak.current_streak > streak.longest_streak:
        streak.longest_streak = streak.current_streak
    
    db.session.commit()
    
    flash('Practice session completed! Great work!', 'success')
    return redirect(url_for('dashboard.dashboard'))
