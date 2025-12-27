"""
Flask routes for Bass Practice application.
"""
from datetime import date, datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from .models import (
    db, UserProfile, Exercise, PracticeSession, SessionExercise, 
    Progress, Song, ChordProgression, EarTrainingExercise, 
    EarTrainingResult, PracticeStreak, QuizResult, DynamicExercise
)
from .quiz_generator import generate_quiz, QUIZ_CATEGORIES
from .exercise_generator import generate_exercise, EXERCISE_CATEGORIES
from .practice_generator import generate_practice_session
from .song_manager import generate_daily_song_playlist, update_song_mastery

main_bp = Blueprint('main', __name__)


# =============================================================================
# Dashboard Routes
# =============================================================================

@main_bp.route('/')
def dashboard():
    """Main dashboard showing practice overview."""
    # Get user profile
    profile = UserProfile.query.first()
    if not profile:
        return redirect(url_for('main.settings'))
    
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
    ).limit(7).all()
    
    # Get progress by category
    progress_data = Progress.query.all()
    
    # Get daily song playlist
    song_playlist = generate_daily_song_playlist()
    
    # Calculate stats
    total_practice_time = db.session.query(
        db.func.sum(PracticeSession.actual_duration)
    ).scalar() or 0
    
    total_sessions = PracticeSession.query.filter_by(is_completed=True).count()
    
    return render_template('dashboard.html',
        profile=profile,
        streak=streak,
        todays_session=todays_session,
        recent_sessions=recent_sessions,
        progress_data=progress_data,
        song_playlist=song_playlist,
        total_practice_time=total_practice_time,
        total_sessions=total_sessions
    )


# =============================================================================
# Practice Session Routes
# =============================================================================

@main_bp.route('/practice/generate', methods=['POST'])
def generate_practice():
    """Generate a new practice session."""
    profile = UserProfile.query.first()
    if not profile:
        flash('Please set up your profile first.', 'warning')
        return redirect(url_for('main.settings'))
    
    # Check if we have exercises in the database
    exercise_count = Exercise.query.count()
    if exercise_count == 0:
        # Force reseed
        from .seed_data import seed_database
        seed_database()
        flash('Exercise database has been initialized.', 'info')
    
    # Check if there's already a session for today
    today = date.today()
    existing_session = PracticeSession.query.filter_by(session_date=today).first()
    
    if existing_session and not existing_session.is_completed:
        return redirect(url_for('main.practice_session', session_id=existing_session.id))
    
    # Generate new session
    session = generate_practice_session(
        skill_level=profile.skill_level,
        duration_minutes=profile.session_duration,
        preferred_genre=profile.preferred_genre
    )
    
    if session.total_exercises == 0:
        flash('Could not generate exercises. Please check the exercise library.', 'warning')
        return redirect(url_for('main.dashboard'))
    
    return redirect(url_for('main.practice_session', session_id=session.id))


@main_bp.route('/practice/<int:session_id>')
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


@main_bp.route('/practice/<int:session_id>/exercise/<int:exercise_index>/complete', methods=['POST'])
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
        progress = Progress.query.filter_by(category=exercise_data.category).first()
        if progress:
            progress.exercises_completed += 1
            progress.last_practiced = date.today()
            if session_exercise.actual_duration:
                progress.total_practice_time += session_exercise.actual_duration
    
    db.session.commit()
    
    return jsonify({'success': True, 'completed': session.completed_exercises})


@main_bp.route('/practice/<int:session_id>/complete', methods=['POST'])
def complete_session(session_id):
    """Complete the entire practice session."""
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
    return redirect(url_for('main.dashboard'))


# =============================================================================
# Exercise Library Routes
# =============================================================================

@main_bp.route('/exercises')
def exercises():
    """Browse all exercises."""
    category = request.args.get('category', '')
    difficulty = request.args.get('difficulty', type=int)
    search = request.args.get('search', '')
    
    query = Exercise.query
    
    if category:
        query = query.filter_by(category=category)
    if difficulty:
        query = query.filter_by(difficulty_level=difficulty)
    if search:
        query = query.filter(Exercise.title.ilike(f'%{search}%'))
    
    exercises = query.order_by(Exercise.category, Exercise.difficulty_level).all()
    
    # Get unique categories for filter
    categories = db.session.query(Exercise.category).distinct().all()
    categories = [c[0] for c in categories]
    
    return render_template('exercises.html',
        exercises=exercises,
        categories=categories,
        current_category=category,
        current_difficulty=difficulty,
        search=search
    )


@main_bp.route('/exercises/<int:exercise_id>')
def exercise_detail(exercise_id):
    """View exercise details."""
    exercise = Exercise.query.get_or_404(exercise_id)
    return render_template('exercise_detail.html', exercise=exercise)


@main_bp.route('/exercises/dynamic/<int:exercise_id>')
def dynamic_exercise_detail(exercise_id):
    """View dynamically generated exercise details."""
    exercise = DynamicExercise.query.get_or_404(exercise_id)
    return render_template('dynamic_exercise_detail.html', exercise=exercise)


@main_bp.route('/exercises/generate')
def generate_new_exercise():
    """Generate a new dynamic exercise."""
    category = request.args.get('category', None)
    difficulty = request.args.get('difficulty', 3, type=int)
    
    if category and category not in EXERCISE_CATEGORIES:
        category = None
    
    exercise_data = generate_exercise(category, difficulty)
    
    return jsonify({
        'title': exercise_data['title'],
        'category': exercise_data['category'],
        'subcategory': exercise_data.get('subcategory', ''),
        'difficulty': exercise_data.get('difficulty', difficulty),
        'duration': exercise_data.get('duration', 5),
        'key': exercise_data.get('key', ''),
        'tempo': exercise_data.get('tempo', 80),
        'description': exercise_data.get('description', ''),
        'instructions': exercise_data.get('instructions', ''),
        'tips': exercise_data.get('tips', ''),
        'tab': exercise_data.get('tab', ''),
        'notes': exercise_data.get('notes', []),
    })


@main_bp.route('/exercises/categories')
def get_exercise_categories():
    """Get available exercise categories."""
    return jsonify({
        'categories': EXERCISE_CATEGORIES
    })


# =============================================================================
# Song Routes
# =============================================================================

@main_bp.route('/songs')
def songs():
    """Browse and manage songs."""
    genre = request.args.get('genre', '')
    mastery = request.args.get('mastery', type=int)
    search = request.args.get('search', '')
    
    query = Song.query
    
    if genre:
        query = query.filter_by(genre=genre)
    if mastery is not None:
        query = query.filter_by(mastery_level=mastery)
    if search:
        query = query.filter(
            db.or_(
                Song.title.ilike(f'%{search}%'),
                Song.artist.ilike(f'%{search}%')
            )
        )
    
    songs = query.order_by(Song.mastery_level, Song.title).all()
    
    # Get daily playlist
    playlist = generate_daily_song_playlist()
    
    # Get unique genres
    genres = db.session.query(Song.genre).distinct().all()
    genres = [g[0] for g in genres if g[0]]
    
    return render_template('songs.html',
        songs=songs,
        playlist=playlist,
        genres=genres,
        current_genre=genre,
        current_mastery=mastery,
        search=search
    )


@main_bp.route('/songs/add', methods=['GET', 'POST'])
def add_song():
    """Add a new song to practice."""
    if request.method == 'POST':
        song = Song(
            title=request.form['title'],
            artist=request.form.get('artist', ''),
            genre=request.form.get('genre', ''),
            difficulty_level=request.form.get('difficulty_level', type=int) or 5,
            key_signature=request.form.get('key_signature', ''),
            tempo_bpm=request.form.get('tempo_bpm', type=int),
            youtube_url=request.form.get('youtube_url', ''),
            practice_notes=request.form.get('practice_notes', '')
        )
        db.session.add(song)
        db.session.commit()
        
        flash(f'Added "{song.title}" to your song library!', 'success')
        return redirect(url_for('main.songs'))
    
    return render_template('song_form.html', song=None)


@main_bp.route('/songs/<int:song_id>/edit', methods=['GET', 'POST'])
def edit_song(song_id):
    """Edit an existing song."""
    song = Song.query.get_or_404(song_id)
    
    if request.method == 'POST':
        song.title = request.form['title']
        song.artist = request.form.get('artist', '')
        song.genre = request.form.get('genre', '')
        song.difficulty_level = request.form.get('difficulty_level', type=int) or 5
        song.key_signature = request.form.get('key_signature', '')
        song.tempo_bpm = request.form.get('tempo_bpm', type=int)
        song.youtube_url = request.form.get('youtube_url', '')
        song.practice_notes = request.form.get('practice_notes', '')
        
        db.session.commit()
        flash('Song updated!', 'success')
        return redirect(url_for('main.songs'))
    
    return render_template('song_form.html', song=song)


@main_bp.route('/songs/<int:song_id>/practice', methods=['POST'])
def practice_song(song_id):
    """Record a song practice session."""
    song = Song.query.get_or_404(song_id)
    quality = request.form.get('quality', type=int) or 3
    
    update_song_mastery(song, quality)
    
    return jsonify({
        'success': True,
        'mastery_level': song.mastery_level,
        'practice_count': song.practice_count
    })


@main_bp.route('/songs/<int:song_id>/delete', methods=['POST'])
def delete_song(song_id):
    """Delete a song."""
    song = Song.query.get_or_404(song_id)
    db.session.delete(song)
    db.session.commit()
    
    flash(f'Deleted "{song.title}" from your library.', 'info')
    return redirect(url_for('main.songs'))


# =============================================================================
# Chord Progression Routes
# =============================================================================

@main_bp.route('/progressions')
def chord_progressions():
    """Browse chord progressions."""
    genre = request.args.get('genre', '')
    
    query = ChordProgression.query
    
    if genre:
        query = query.filter_by(genre=genre)
    
    progressions = query.order_by(ChordProgression.difficulty_level).all()
    
    # Get unique genres
    genres = db.session.query(ChordProgression.genre).distinct().all()
    genres = [g[0] for g in genres if g[0]]
    
    return render_template('chord_progressions.html',
        progressions=progressions,
        genres=genres,
        current_genre=genre
    )


@main_bp.route('/progressions/<int:progression_id>')
def progression_detail(progression_id):
    """View chord progression details."""
    progression = ChordProgression.query.get_or_404(progression_id)
    
    # Find songs using this progression
    related_songs = Song.query.filter(
        Song.chord_progression.ilike(f'%{progression.numerals}%')
    ).all()
    
    return render_template('progression_detail.html',
        progression=progression,
        related_songs=related_songs
    )


# =============================================================================
# Ear Training Routes
# =============================================================================

@main_bp.route('/ear-training')
def ear_training():
    """Ear training main page."""
    exercise_type = request.args.get('type', 'interval')
    
    # Get exercise stats
    total_attempts = EarTrainingResult.query.count()
    correct_attempts = EarTrainingResult.query.filter_by(correct=True).count()
    accuracy = (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0
    
    # Get recent results
    recent_results = EarTrainingResult.query.order_by(
        EarTrainingResult.practiced_at.desc()
    ).limit(10).all()
    
    return render_template('ear_training.html',
        exercise_type=exercise_type,
        total_attempts=total_attempts,
        accuracy=accuracy,
        recent_results=recent_results
    )


def calculate_adaptive_difficulty(exercise_type):
    """Calculate difficulty based on recent performance."""
    # Get last 10 results for this exercise type
    recent_results = EarTrainingResult.query.join(EarTrainingExercise).filter(
        EarTrainingExercise.exercise_type == exercise_type
    ).order_by(EarTrainingResult.practiced_at.desc()).limit(10).all()
    
    if not recent_results:
        return 1  # Start at level 1
    
    # Calculate accuracy of recent attempts
    correct_count = sum(1 for r in recent_results if r.correct)
    accuracy = correct_count / len(recent_results)
    
    # Get current average difficulty of recent exercises
    recent_exercises = [r.exercise for r in recent_results]
    avg_difficulty = sum(e.difficulty_level for e in recent_exercises) / len(recent_exercises)
    
    # Adjust difficulty based on accuracy
    if accuracy >= 0.8:  # 80%+ correct - increase difficulty
        new_difficulty = min(5, int(avg_difficulty) + 1)
    elif accuracy <= 0.4:  # 40% or less - decrease difficulty
        new_difficulty = max(1, int(avg_difficulty) - 1)
    else:  # Stay at current level
        new_difficulty = max(1, int(avg_difficulty))
    
    return new_difficulty


@main_bp.route('/ear-training/exercise')
def get_ear_training_exercise():
    """Get a new ear training exercise with adaptive difficulty."""
    exercise_type = request.args.get('type', 'interval')
    
    # Calculate adaptive difficulty
    difficulty = calculate_adaptive_difficulty(exercise_type)
    
    # Get exercises at or below the calculated difficulty
    exercise = EarTrainingExercise.query.filter_by(
        exercise_type=exercise_type
    ).filter(
        EarTrainingExercise.difficulty_level <= difficulty
    ).order_by(db.func.random()).first()
    
    if not exercise:
        return jsonify({'error': 'No exercises found'}), 404
    
    return jsonify({
        'id': exercise.id,
        'type': exercise.exercise_type,
        'title': exercise.title,
        'description': exercise.description,
        'options': exercise.options,
        'root_note': exercise.root_note,
        'hints': exercise.hints,
        'difficulty': difficulty  # Send current difficulty level for display
    })


@main_bp.route('/ear-training/play/<int:exercise_id>')
def get_ear_training_audio(exercise_id):
    """Get audio data for an exercise without revealing the answer."""
    exercise = EarTrainingExercise.query.get_or_404(exercise_id)
    
    # Interval semitones mapping
    intervals = {
        'm2': 1, 'M2': 2, 'm3': 3, 'M3': 4, 'P4': 5,
        'tritone': 6, 'P5': 7, 'm6': 8, 'M6': 9, 'm7': 10, 'M7': 11, 'P8': 12
    }
    
    # Chord type to semitones mapping
    chord_types = {
        'major': [0, 4, 7],
        'minor': [0, 3, 7],
        'diminished': [0, 3, 6],
        'augmented': [0, 4, 8],
        'major7': [0, 4, 7, 11],
        'minor7': [0, 3, 7, 10],
        'dominant7': [0, 4, 7, 10],
        'diminished7': [0, 3, 6, 9]
    }
    
    # Scale degree to semitones (for melody exercises)
    scale_degrees = {
        '1': 0, '2': 2, '3': 4, '4': 5, '5': 7, '6': 9, '7': 11, '8': 12,
        'b2': 1, 'b3': 3, 'b5': 6, 'b6': 8, 'b7': 10,
        '#4': 6, '#5': 8
    }
    
    answer = exercise.correct_answer
    exercise_type = exercise.exercise_type
    
    if exercise_type == 'interval':
        semitones = intervals.get(answer)
        if semitones is not None:
            return jsonify({'type': 'interval', 'semitones': semitones})
    
    elif exercise_type == 'chord':
        semitones = chord_types.get(answer)
        if semitones is not None:
            return jsonify({'type': 'chord', 'semitones': semitones})
    
    elif exercise_type == 'melody':
        # Parse melody pattern like "1-3-5-3" or "1-b3-5-b7"
        pattern = answer.split('-')
        semitones = []
        for degree in pattern:
            s = scale_degrees.get(degree.strip())
            if s is not None:
                semitones.append(s)
        if semitones:
            return jsonify({'type': 'melody', 'semitones': semitones})
    
    return jsonify({'error': 'Cannot generate audio for this exercise'}), 400


@main_bp.route('/ear-training/submit', methods=['POST'])
def submit_ear_training_answer():
    """Submit an ear training answer."""
    data = request.get_json()
    
    exercise_id = data.get('exercise_id')
    user_answer = data.get('answer')
    response_time = data.get('response_time')
    
    exercise = EarTrainingExercise.query.get_or_404(exercise_id)
    correct = user_answer == exercise.correct_answer
    
    result = EarTrainingResult(
        exercise_id=exercise_id,
        user_answer=user_answer,
        correct=correct,
        response_time_ms=response_time
    )
    db.session.add(result)
    db.session.commit()
    
    return jsonify({
        'correct': correct,
        'correct_answer': exercise.correct_answer
    })


# =============================================================================
# Quiz Routes
# =============================================================================

# Store generated questions temporarily for answer validation
_quiz_cache = {}


def calculate_quiz_difficulty(quiz_category):
    """Calculate adaptive difficulty based on recent quiz performance."""
    recent_results = QuizResult.query.filter_by(
        quiz_type=quiz_category
    ).order_by(QuizResult.attempted_at.desc()).limit(10).all()
    
    if not recent_results:
        return 1
    
    correct_count = sum(1 for r in recent_results if r.correct)
    accuracy = correct_count / len(recent_results)
    
    # Estimate difficulty from performance
    if accuracy >= 0.8:
        return min(5, len(recent_results) // 2 + 1)
    elif accuracy <= 0.4:
        return max(1, len(recent_results) // 3)
    return max(1, min(5, int(len(recent_results) / 2)))


@main_bp.route('/quiz')
def quiz():
    """Quiz main page."""
    quiz_category = request.args.get('type', 'fretboard')
    
    # Get stats for each quiz category
    quiz_categories = list(QUIZ_CATEGORIES.keys())
    stats = {}
    
    for cat in quiz_categories:
        total = QuizResult.query.filter_by(quiz_type=cat).count()
        correct = QuizResult.query.filter_by(quiz_type=cat, correct=True).count()
        stats[cat] = {
            'total': total,
            'correct': correct,
            'accuracy': (correct / total * 100) if total > 0 else 0
        }
    
    # Overall stats
    total_attempts = QuizResult.query.count()
    correct_attempts = QuizResult.query.filter_by(correct=True).count()
    overall_accuracy = (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0
    
    # Recent results
    recent_results = QuizResult.query.order_by(
        QuizResult.attempted_at.desc()
    ).limit(10).all()
    
    return render_template('quiz.html',
        quiz_type=quiz_category,
        quiz_categories=quiz_categories,
        stats=stats,
        total_attempts=total_attempts,
        overall_accuracy=overall_accuracy,
        recent_results=recent_results
    )


@main_bp.route('/quiz/question')
def get_quiz_question():
    """Generate a dynamic quiz question."""
    import uuid
    
    quiz_category = request.args.get('type', 'fretboard')
    difficulty = calculate_quiz_difficulty(quiz_category)
    
    # Generate a new question
    question = generate_quiz(quiz_category, difficulty)
    
    # Generate a unique ID for this question
    question_id = str(uuid.uuid4())
    
    # Cache the question for answer validation
    _quiz_cache[question_id] = {
        'correct_answer': question['correct_answer'],
        'explanation': question.get('explanation', ''),
        'quiz_type': quiz_category,
    }
    
    # Clean old cache entries (keep last 100)
    if len(_quiz_cache) > 100:
        keys = list(_quiz_cache.keys())
        for key in keys[:-100]:
            del _quiz_cache[key]
    
    return jsonify({
        'id': question_id,
        'type': question['type'],
        'category': quiz_category,
        'title': question['title'],
        'question': question['question'],
        'options': question['options'],
        'difficulty': question.get('difficulty', difficulty),
        'string_number': question.get('string_number'),
        'fret_number': question.get('fret_number'),
    })


@main_bp.route('/quiz/submit', methods=['POST'])
def submit_quiz_answer():
    """Submit a quiz answer."""
    data = request.get_json()
    
    question_id = data.get('quiz_id')
    user_answer = data.get('answer')
    response_time = data.get('response_time')
    
    # Get question from cache
    cached = _quiz_cache.get(question_id)
    if not cached:
        return jsonify({'error': 'Question expired, please try again'}), 400
    
    correct = user_answer == cached['correct_answer']
    
    # Save result
    result = QuizResult(
        quiz_id=0,  # Dynamic questions don't have DB IDs
        quiz_type=cached['quiz_type'],
        user_answer=user_answer,
        correct=correct,
        response_time_ms=response_time
    )
    db.session.add(result)
    db.session.commit()
    
    # Clean up cache
    del _quiz_cache[question_id]
    
    return jsonify({
        'correct': correct,
        'correct_answer': cached['correct_answer'],
        'explanation': cached['explanation']
    })


# =============================================================================
# Progress Routes
# =============================================================================

@main_bp.route('/progress')
def progress():
    """View detailed progress statistics."""
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
    
    # Get ear training stats
    ear_stats = {}
    for exercise_type in ['interval', 'chord', 'melody']:
        total = EarTrainingResult.query.join(EarTrainingExercise).filter(
            EarTrainingExercise.exercise_type == exercise_type
        ).count()
        correct = EarTrainingResult.query.join(EarTrainingExercise).filter(
            EarTrainingExercise.exercise_type == exercise_type,
            EarTrainingResult.correct == True
        ).count()
        ear_stats[exercise_type] = {
            'total': total,
            'correct': correct,
            'accuracy': (correct / total * 100) if total > 0 else 0
        }
    
    # Get song progress
    total_songs = Song.query.count()
    mastered_songs = Song.query.filter(Song.mastery_level >= 4).count()
    
    return render_template('progress.html',
        progress_data=progress_data,
        sessions=sessions,
        streak=streak,
        weekly_time=weekly_time,
        ear_stats=ear_stats,
        total_songs=total_songs,
        mastered_songs=mastered_songs
    )


# =============================================================================
# Settings Routes
# =============================================================================

@main_bp.route('/settings', methods=['GET', 'POST'])
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
        return redirect(url_for('main.dashboard'))
    
    return render_template('settings.html', profile=profile)


# =============================================================================
# Debug / Admin Routes
# =============================================================================

@main_bp.route('/admin/reseed', methods=['POST'])
def reseed_database():
    """Force reseed the database with initial data."""
    from .seed_data import seed_exercises, seed_chord_progressions, seed_ear_training_exercises, seed_progress
    
    # Clear existing data
    Exercise.query.delete()
    ChordProgression.query.delete()
    EarTrainingExercise.query.delete()
    
    # Reseed
    seed_exercises()
    seed_chord_progressions()
    seed_ear_training_exercises()
    seed_progress()
    
    db.session.commit()
    
    flash(f'Database reseeded! {Exercise.query.count()} exercises added.', 'success')
    return redirect(url_for('main.dashboard'))


@main_bp.route('/admin/status')
def database_status():
    """Check database status."""
    status = {
        'exercises': Exercise.query.count(),
        'exercises_by_category': {},
        'chord_progressions': ChordProgression.query.count(),
        'ear_training_exercises': EarTrainingExercise.query.count(),
        'practice_sessions': PracticeSession.query.count(),
        'songs': Song.query.count(),
        'user_profile': UserProfile.query.first() is not None
    }
    
    # Get exercise count by category
    categories = db.session.query(Exercise.category, db.func.count(Exercise.id)).group_by(Exercise.category).all()
    status['exercises_by_category'] = {cat: count for cat, count in categories}
    
    return jsonify(status)


# =============================================================================
# API Routes for AJAX
# =============================================================================

@main_bp.route('/api/progress-data')
def api_progress_data():
    """Get progress data for charts."""
    # Get practice time by date for last 30 days
    thirty_days_ago = date.today() - timedelta(days=30)
    
    sessions = PracticeSession.query.filter(
        PracticeSession.session_date >= thirty_days_ago,
        PracticeSession.is_completed == True
    ).all()
    
    daily_data = {}
    for session in sessions:
        date_str = session.session_date.isoformat()
        daily_data[date_str] = daily_data.get(date_str, 0) + (session.actual_duration or 0)
    
    # Get progress by category
    categories = Progress.query.all()
    category_data = {p.category: p.skill_level for p in categories}
    
    return jsonify({
        'daily_practice': daily_data,
        'category_progress': category_data
    })
