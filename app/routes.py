"""
Flask routes for Bass Practice application.
"""
from datetime import date, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from .models import (
    db, UserProfile, Exercise, PracticeSession, SessionExercise, 
    Progress, Song, ChordProgression, EarTrainingExercise, 
    EarTrainingResult, PracticeStreak, QuizResult, DynamicExercise,
    TimingSession, TimingHighScore
)
from .quiz_generator import generate_quiz, QUIZ_CATEGORIES
from .exercise_generator import generate_exercise, EXERCISE_CATEGORIES
from .practice_generator import generate_practice_session
from .song_manager import generate_daily_song_playlist, update_song_mastery
from .ear_training_generator import generate_ear_training_exercise
from .song_suggestion import generate_song_suggestion, get_available_providers
from .timing_practice_generator import (
    generate_timing_exercise, calculate_hit_quality, calculate_session_score,
    generate_practice_tips, GAME_MODES, DIFFICULTY_LEVELS
)

main_bp = Blueprint('main', __name__)


# =============================================================================
# Helper Functions
# =============================================================================

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
    # Use a logarithmic curve: faster growth at first, slower as you progress
    # Formula: skill_level = 1 - (1 / (1 + exercises / 10))
    # This gives: 1 exercise = ~9%, 5 = ~33%, 10 = ~50%, 20 = ~67%, 50 = ~83%, 100+ = ~91%+
    exercises = progress.exercises_completed
    if exercises <= 0:
        progress.skill_level = 0.0
    else:
        # Logarithmic growth curve
        progress.skill_level = min(1.0, 1.0 - (1.0 / (1.0 + exercises / 10.0)))
    
    db.session.commit()
    return progress


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
        duration = session_exercise.actual_duration or 0
        update_progress_for_category(exercise_data.category, duration)
    
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


@main_bp.route('/exercises/complete', methods=['POST'])
def complete_individual_exercise():
    """Track completion of an individual exercise (not in a practice session)."""
    data = request.get_json()
    
    category = data.get('category')
    duration = data.get('duration', 0)  # Optional duration in minutes
    
    if not category or category not in EXERCISE_CATEGORIES:
        return jsonify({'error': 'Invalid category'}), 400
    
    # Update progress for this category
    progress = update_progress_for_category(category, duration)
    
    return jsonify({
        'success': True,
        'category': category,
        'skill_level': progress.skill_level,
        'exercises_completed': progress.exercises_completed
    })


@main_bp.route('/exercises/recommended')
def get_recommended_exercise():
    """Generate a recommended exercise based on lowest skill level."""
    # Get progress by category
    progress_data = Progress.query.all()
    
    # Find the category with the lowest skill level
    if progress_data:
        lowest_progress = min(progress_data, key=lambda p: p.skill_level)
        category = lowest_progress.category
        # Use skill level to determine difficulty (convert 0.0-1.0 to 1-5)
        difficulty = max(1, min(5, int(lowest_progress.skill_level * 5) + 1))
    else:
        # If no progress yet, start with scales at difficulty 1
        category = 'scales'
        difficulty = 1
    
    # Generate exercise data
    exercise_data = generate_exercise(category, difficulty)
    
    # Create a DynamicExercise record
    dynamic_exercise = DynamicExercise(
        title=exercise_data['title'],
        category=exercise_data['category'],
        subcategory=exercise_data.get('subcategory', ''),
        difficulty_level=exercise_data.get('difficulty', difficulty),
        estimated_duration=exercise_data.get('duration', 5),
        instructions=exercise_data.get('instructions', ''),
        tips=exercise_data.get('tips', ''),
        description=exercise_data.get('description', ''),
        key_signature=exercise_data.get('key', ''),
        tempo_bpm=exercise_data.get('tempo', 80),
        tab_notation=exercise_data.get('tab', ''),
        notes_data=str(exercise_data.get('notes', [])),
    )
    db.session.add(dynamic_exercise)
    db.session.commit()
    
    # Redirect to the exercise detail page
    return redirect(url_for('main.dynamic_exercise_detail', exercise_id=dynamic_exercise.id))


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


@main_bp.route('/songs/suggest')
def suggest_song():
    """Get an AI-powered song suggestion based on library and skills."""
    provider = request.args.get('provider', 'groq')
    model = request.args.get('model', None)
    level = request.args.get('level', type=int)
    genre = request.args.get('genre', None)
    custom_instructions = request.args.get('custom_instructions', None)
    
    result = generate_song_suggestion(
        provider_id=provider, 
        model_id=model,
        level=level,
        genre=genre,
        custom_instructions=custom_instructions
    )
    return jsonify(result)


@main_bp.route('/songs/providers')
def get_llm_providers():
    """Get available LLM providers and their models."""
    providers = get_available_providers()
    return jsonify({'providers': providers})


@main_bp.route('/songs/add-suggestion', methods=['POST'])
def add_suggested_song():
    """Add a suggested song to the library."""
    data = request.get_json()
    
    song = Song(
        title=data.get('title', ''),
        artist=data.get('artist', ''),
        genre=data.get('genre', ''),
        difficulty_level=data.get('difficulty_level', 5),
        key_signature=data.get('key_signature', ''),
        tempo_bpm=data.get('tempo_bpm'),
        practice_notes=data.get('reason', '')  # Store reason as practice notes
    )
    db.session.add(song)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'song_id': song.id,
        'message': f'Added "{song.title}" to your library!'
    })


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
    
    # Get exercise stats (only for dynamic exercises, exercise_id=0)
    total_attempts = EarTrainingResult.query.filter_by(exercise_id=0).count()
    correct_attempts = EarTrainingResult.query.filter_by(exercise_id=0, correct=True).count()
    accuracy = (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0
    
    # Get recent results
    recent_results = EarTrainingResult.query.filter_by(exercise_id=0).order_by(
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
    # Note: Since exercises are now dynamic, we use the stored difficulty in results
    recent_results = EarTrainingResult.query.filter(
        EarTrainingResult.exercise_id == 0  # Dynamic exercises use 0 as ID
    ).order_by(EarTrainingResult.practiced_at.desc()).limit(10).all()
    
    if not recent_results:
        return 1  # Start at level 1
    
    # Calculate accuracy of recent attempts
    correct_count = sum(1 for r in recent_results if r.correct)
    accuracy = correct_count / len(recent_results)
    
    # Get difficulty from cache if available, otherwise estimate from results
    # We'll track difficulty in the cache, but for now estimate from performance
    estimated_difficulty = 2  # Default
    
    # Adjust difficulty based on accuracy
    if accuracy >= 0.8:  # 80%+ correct - increase difficulty
        new_difficulty = min(5, estimated_difficulty + 1)
    elif accuracy <= 0.4:  # 40% or less - decrease difficulty
        new_difficulty = max(1, estimated_difficulty - 1)
    else:  # Stay at current level
        new_difficulty = max(1, estimated_difficulty)
    
    return new_difficulty


@main_bp.route('/ear-training/exercise')
def get_ear_training_exercise():
    """Get a new ear training exercise with adaptive difficulty."""
    import uuid
    
    exercise_type = request.args.get('type', 'interval')
    
    # Calculate adaptive difficulty
    difficulty = calculate_adaptive_difficulty(exercise_type)
    
    # Generate a new exercise dynamically
    exercise_data = generate_ear_training_exercise(exercise_type, difficulty)
    
    # Generate a unique ID for this exercise
    exercise_id = str(uuid.uuid4())
    
    # Cache the exercise for answer validation
    _ear_training_cache[exercise_id] = {
        'correct_answer': exercise_data['correct_answer'],
        'exercise_type': exercise_type,
        'difficulty': difficulty,
        'root_note': exercise_data.get('root_note', 'C'),
    }
    
    # Clean old cache entries (keep last 100)
    if len(_ear_training_cache) > 100:
        keys = list(_ear_training_cache.keys())
        for key in keys[:-100]:
            del _ear_training_cache[key]
    
    return jsonify({
        'id': exercise_id,
        'type': exercise_data['type'],
        'title': exercise_data['title'],
        'description': exercise_data['description'],
        'options': exercise_data['options'],
        'root_note': exercise_data['root_note'],
        'hints': exercise_data['hints'],
        'difficulty': difficulty
    })


@main_bp.route('/ear-training/play/<exercise_id>')
def get_ear_training_audio(exercise_id):
    """Get audio data for an exercise without revealing the answer."""
    # Get exercise from cache
    cached = _ear_training_cache.get(exercise_id)
    if not cached:
        return jsonify({'error': 'Exercise not found'}), 404
    
    answer = cached['correct_answer']
    exercise_type = cached['exercise_type']
    root_note = cached.get('root_note', 'C')
    
    # Import constants from ear_training_generator
    from .ear_training_generator import INTERVALS, CHORD_FORMULAS, SCALE_DEGREES
    
    if exercise_type == 'interval':
        semitones = INTERVALS.get(answer)
        if semitones is not None:
            return jsonify({'type': 'interval', 'semitones': semitones, 'root_note': root_note})
    
    elif exercise_type == 'chord':
        semitones = CHORD_FORMULAS.get(answer)
        if semitones is not None:
            return jsonify({'type': 'chord', 'semitones': semitones, 'root_note': root_note})
    
    elif exercise_type == 'melody':
        # Parse melody pattern like "1-3-5-3" or "1-b3-5-b7"
        pattern = answer.split('-')
        semitones = []
        for degree in pattern:
            s = SCALE_DEGREES.get(degree.strip())
            if s is not None:
                semitones.append(s)
        if semitones:
            return jsonify({'type': 'melody', 'semitones': semitones, 'root_note': root_note})
    
    return jsonify({'error': 'Cannot generate audio for this exercise'}), 400


@main_bp.route('/ear-training/submit', methods=['POST'])
def submit_ear_training_answer():
    """Submit an ear training answer."""
    data = request.get_json()
    
    exercise_id = data.get('exercise_id')
    user_answer = data.get('answer')
    response_time = data.get('response_time')
    
    # Get exercise from cache
    cached = _ear_training_cache.get(exercise_id)
    if not cached:
        return jsonify({'error': 'Exercise expired, please try again'}), 400
    
    correct = user_answer == cached['correct_answer']
    
    # Save result (using exercise_id=0 for dynamic exercises)
    result = EarTrainingResult(
        exercise_id=0,  # Dynamic exercises don't have DB IDs
        user_answer=user_answer,
        correct=correct,
        response_time_ms=response_time
    )
    db.session.add(result)
    db.session.commit()
    
    # Update progress for theory category when exercise is completed
    # Ear training exercises (intervals, chords, melodies) are theory-related
    if correct:
        # Only count correct answers toward progress
        update_progress_for_category('theory', duration_minutes=0)
    
    # Clean up cache
    del _ear_training_cache[exercise_id]
    
    return jsonify({
        'correct': correct,
        'correct_answer': cached['correct_answer']
    })


# =============================================================================
# Quiz Routes
# =============================================================================

# Store generated questions temporarily for answer validation
_quiz_cache = {}

# Store generated ear training exercises temporarily for answer validation
_ear_training_cache = {}


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
    from .seed_data import seed_exercises, seed_chord_progressions, seed_progress
    
    # Clear existing data
    Exercise.query.delete()
    ChordProgression.query.delete()
    # Note: EarTrainingExercise seeding removed - exercises are now dynamically generated
    
    # Reseed
    seed_exercises()
    seed_chord_progressions()
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
        'ear_training_exercises': 'Dynamic (not stored in DB)',
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


# =============================================================================
# Timing Practice Routes
# =============================================================================

# Store active timing exercises
_timing_cache = {}


@main_bp.route('/timing')
def timing_practice():
    """Timing practice main page with game selection."""
    # Get high scores for each game mode
    high_scores = {}
    for mode in GAME_MODES.keys():
        best = TimingHighScore.query.filter_by(game_mode=mode).order_by(
            TimingHighScore.high_score.desc()
        ).first()
        high_scores[mode] = best
    
    # Get recent sessions
    recent_sessions = TimingSession.query.order_by(
        TimingSession.created_at.desc()
    ).limit(10).all()
    
    # Calculate overall stats
    total_sessions = TimingSession.query.count()
    total_notes = db.session.query(db.func.sum(TimingSession.total_notes)).scalar() or 0
    total_perfect = db.session.query(db.func.sum(TimingSession.perfect_hits)).scalar() or 0
    overall_accuracy = round(total_perfect / total_notes * 100, 1) if total_notes > 0 else 0
    
    # Get best streak across all sessions
    best_session = TimingSession.query.order_by(TimingSession.score.desc()).first()
    
    return render_template('timing_practice.html',
        game_modes=GAME_MODES,
        difficulty_levels=DIFFICULTY_LEVELS,
        high_scores=high_scores,
        recent_sessions=recent_sessions,
        total_sessions=total_sessions,
        total_notes=total_notes,
        overall_accuracy=overall_accuracy,
        best_session=best_session
    )


@main_bp.route('/timing/start', methods=['POST'])
def start_timing_game():
    """Start a new timing practice game."""
    import uuid
    
    data = request.get_json()
    game_mode = data.get('game_mode', 'groove')
    difficulty = data.get('difficulty', 1)
    tempo = data.get('tempo')  # Optional custom tempo
    duration_bars = data.get('duration_bars', 8)
    
    # Generate the exercise
    exercise = generate_timing_exercise(
        game_mode=game_mode,
        difficulty=difficulty,
        tempo=tempo,
        duration_bars=duration_bars
    )
    
    # Create a unique session ID
    session_id = str(uuid.uuid4())
    
    # Cache the exercise configuration
    _timing_cache[session_id] = {
        'exercise': exercise,
        'hits': [],
        'started_at': None,
        'current_note_index': 0,
    }
    
    # Clean old cache entries
    if len(_timing_cache) > 50:
        keys = list(_timing_cache.keys())
        for key in keys[:-50]:
            del _timing_cache[key]
    
    return jsonify({
        'session_id': session_id,
        'game_mode': exercise['game_mode'],
        'mode_name': exercise['mode_name'],
        'mode_description': exercise['mode_description'],
        'difficulty': exercise['difficulty'],
        'difficulty_name': exercise['difficulty_name'],
        'tempo': exercise['tempo'],
        'perfect_window_ms': exercise['perfect_window_ms'],
        'good_window_ms': exercise['good_window_ms'],
        'total_notes': exercise['total_notes'],
        'duration_ms': exercise['duration_ms'],
        'beat_times': exercise['beat_times'],
    })


@main_bp.route('/timing/hit', methods=['POST'])
def register_timing_hit():
    """Register a note hit from the player."""
    data = request.get_json()
    session_id = data.get('session_id')
    hit_time_ms = data.get('hit_time_ms')
    note_index = data.get('note_index')
    
    cached = _timing_cache.get(session_id)
    if not cached:
        return jsonify({'error': 'Session not found'}), 404
    
    exercise = cached['exercise']
    beat_times = exercise['beat_times']
    
    if note_index >= len(beat_times):
        return jsonify({'error': 'Invalid note index'}), 400
    
    # Calculate timing offset
    expected_time = beat_times[note_index]
    offset_ms = hit_time_ms - expected_time
    
    # Determine hit quality
    quality, score, is_early = calculate_hit_quality(
        offset_ms,
        exercise['perfect_window_ms'],
        exercise['good_window_ms']
    )
    
    # Record the hit
    hit_record = {
        'note_index': note_index,
        'expected_time': expected_time,
        'hit_time': hit_time_ms,
        'offset_ms': offset_ms,
        'quality': quality,
        'score': score,
    }
    cached['hits'].append(hit_record)
    
    # Calculate current streak
    streak = 0
    for h in reversed(cached['hits']):
        if h['quality'] in ('perfect', 'good'):
            streak += 1
        else:
            break
    
    return jsonify({
        'quality': quality,
        'score': score,
        'offset_ms': round(offset_ms, 1),
        'is_early': is_early,
        'streak': streak,
    })


@main_bp.route('/timing/miss', methods=['POST'])
def register_timing_miss():
    """Register a missed note."""
    data = request.get_json()
    session_id = data.get('session_id')
    note_index = data.get('note_index')
    
    cached = _timing_cache.get(session_id)
    if not cached:
        return jsonify({'error': 'Session not found'}), 404
    
    exercise = cached['exercise']
    beat_times = exercise['beat_times']
    
    if note_index >= len(beat_times):
        return jsonify({'error': 'Invalid note index'}), 400
    
    # Record the miss
    hit_record = {
        'note_index': note_index,
        'expected_time': beat_times[note_index],
        'hit_time': None,
        'offset_ms': None,
        'quality': 'miss',
        'score': 0,
    }
    cached['hits'].append(hit_record)
    
    return jsonify({'quality': 'miss', 'score': 0, 'streak': 0})


@main_bp.route('/timing/complete', methods=['POST'])
def complete_timing_game():
    """Complete a timing practice game and save results."""
    data = request.get_json()
    session_id = data.get('session_id')
    duration_seconds = data.get('duration_seconds', 0)
    
    cached = _timing_cache.get(session_id)
    if not cached:
        return jsonify({'error': 'Session not found'}), 404
    
    exercise = cached['exercise']
    hits = cached['hits']
    
    # Calculate final stats
    stats = calculate_session_score(hits)
    
    # Generate tips
    tips = generate_practice_tips(stats)
    
    # Save session to database
    timing_session = TimingSession(
        tempo_bpm=exercise['tempo'],
        game_mode=exercise['game_mode'],
        difficulty=exercise['difficulty'],
        total_notes=stats['total_notes'],
        perfect_hits=stats['perfect_hits'],
        good_hits=stats['good_hits'],
        early_hits=stats['early_hits'],
        late_hits=stats['late_hits'],
        missed_notes=stats['missed_notes'],
        average_timing_ms=stats['average_timing_ms'],
        score=stats['total_score'],
        duration_seconds=duration_seconds,
    )
    db.session.add(timing_session)
    
    # Check and update high score
    high_score = TimingHighScore.query.filter_by(
        game_mode=exercise['game_mode'],
        tempo_bpm=exercise['tempo'],
        difficulty=exercise['difficulty']
    ).first()
    
    is_new_high_score = False
    if high_score:
        if stats['total_score'] > high_score.high_score:
            high_score.high_score = stats['total_score']
            high_score.best_accuracy = stats['accuracy_percentage']
            high_score.best_streak = stats['best_streak']
            high_score.achieved_at = db.func.now()
            is_new_high_score = True
    else:
        high_score = TimingHighScore(
            game_mode=exercise['game_mode'],
            tempo_bpm=exercise['tempo'],
            difficulty=exercise['difficulty'],
            high_score=stats['total_score'],
            best_accuracy=stats['accuracy_percentage'],
            best_streak=stats['best_streak'],
        )
        db.session.add(high_score)
        is_new_high_score = True
    
    # Update rhythm progress
    update_progress_for_category('rhythm', duration_minutes=max(1, duration_seconds // 60))
    
    db.session.commit()
    
    # Clean up cache
    del _timing_cache[session_id]
    
    return jsonify({
        'success': True,
        'session_id': timing_session.id,
        'stats': stats,
        'tips': tips,
        'is_new_high_score': is_new_high_score,
        'high_score': high_score.high_score if high_score else stats['total_score'],
    })


@main_bp.route('/timing/history')
def timing_history():
    """Get timing practice history."""
    limit = request.args.get('limit', 20, type=int)
    game_mode = request.args.get('game_mode')
    
    query = TimingSession.query
    if game_mode:
        query = query.filter_by(game_mode=game_mode)
    
    sessions = query.order_by(TimingSession.created_at.desc()).limit(limit).all()
    
    return jsonify({
        'sessions': [{
            'id': s.id,
            'date': s.session_date.isoformat(),
            'game_mode': s.game_mode,
            'tempo': s.tempo_bpm,
            'difficulty': s.difficulty,
            'score': s.score,
            'accuracy': s.accuracy_percentage,
            'perfect_percentage': s.perfect_percentage,
            'total_notes': s.total_notes,
        } for s in sessions]
    })


@main_bp.route('/timing/leaderboard')
def timing_leaderboard():
    """Get high scores leaderboard."""
    game_mode = request.args.get('game_mode')
    
    query = TimingHighScore.query
    if game_mode:
        query = query.filter_by(game_mode=game_mode)
    
    scores = query.order_by(TimingHighScore.high_score.desc()).limit(10).all()
    
    return jsonify({
        'scores': [{
            'game_mode': s.game_mode,
            'tempo': s.tempo_bpm,
            'difficulty': s.difficulty,
            'high_score': s.high_score,
            'best_accuracy': s.best_accuracy,
            'best_streak': s.best_streak,
            'achieved_at': s.achieved_at.isoformat() if s.achieved_at else None,
        } for s in scores]
    })
