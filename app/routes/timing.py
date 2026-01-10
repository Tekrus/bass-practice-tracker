from flask import Blueprint, render_template, request, jsonify
from ..models import db, TimingSession, TimingHighScore
from ..timing_practice_generator import (
    generate_timing_exercise, calculate_session_score,
    generate_practice_tips, GAME_MODES, DIFFICULTY_LEVELS
)
from ..utils.database import update_progress_for_category

bp = Blueprint('timing', __name__)

# Store active timing exercises
_timing_cache = {}

@bp.route('/timing')
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


@bp.route('/timing/start', methods=['POST'])
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
        'started_at': None,
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


@bp.route('/timing/complete', methods=['POST'])
def complete_timing_game():
    """Complete a timing practice game and save results."""
    data = request.get_json()
    session_id = data.get('session_id')
    duration_seconds = data.get('duration_seconds', 0)
    hits = data.get('hits', [])  # Receive hits from client
    
    cached = _timing_cache.get(session_id)
    if not cached:
        return jsonify({'error': 'Session not found'}), 404
    
    exercise = cached['exercise']
    
    # Calculate final stats from client-submitted hits
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
        good_hits=stats['good_hits'] + stats.get('ok_hits', 0),
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


@bp.route('/timing/history')
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


@bp.route('/timing/leaderboard')
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
