from flask import Blueprint, render_template, request, jsonify
from ..models import db, EarTrainingResult
from ..ear_training_generator import generate_ear_training_exercise
from ..utils.database import update_progress_for_category

bp = Blueprint('ear_training', __name__)

# Store generated ear training exercises temporarily for answer validation
_ear_training_cache = {}

@bp.route('/ear-training')
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
    recent_results = EarTrainingResult.query.filter(
        EarTrainingResult.exercise_id == 0
    ).order_by(EarTrainingResult.practiced_at.desc()).limit(10).all()
    
    if not recent_results:
        return 1
    
    correct_count = sum(1 for r in recent_results if r.correct)
    accuracy = correct_count / len(recent_results)
    
    estimated_difficulty = 2
    
    if accuracy >= 0.8:
        new_difficulty = min(5, estimated_difficulty + 1)
    elif accuracy <= 0.4:
        new_difficulty = max(1, estimated_difficulty - 1)
    else:
        new_difficulty = max(1, estimated_difficulty)
    
    return new_difficulty


@bp.route('/ear-training/exercise')
def get_ear_training_exercise():
    """Get a new ear training exercise with adaptive difficulty."""
    import uuid
    
    exercise_type = request.args.get('type', 'interval')
    difficulty = calculate_adaptive_difficulty(exercise_type)
    exercise_data = generate_ear_training_exercise(exercise_type, difficulty)
    
    exercise_id = str(uuid.uuid4())
    
    _ear_training_cache[exercise_id] = {
        'correct_answer': exercise_data['correct_answer'],
        'exercise_type': exercise_type,
        'difficulty': difficulty,
        'root_note': exercise_data.get('root_note', 'C'),
    }
    
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


@bp.route('/ear-training/play/<exercise_id>')
def get_ear_training_audio(exercise_id):
    """Get audio data for an exercise without revealing the answer."""
    cached = _ear_training_cache.get(exercise_id)
    if not cached:
        return jsonify({'error': 'Exercise not found'}), 404
    
    answer = cached['correct_answer']
    exercise_type = cached['exercise_type']
    root_note = cached.get('root_note', 'C')
    
    from ..ear_training_generator import INTERVALS, CHORD_FORMULAS, SCALE_DEGREES
    
    if exercise_type == 'interval':
        semitones = INTERVALS.get(answer)
        if semitones is not None:
            return jsonify({'type': 'interval', 'semitones': semitones, 'root_note': root_note})
    
    elif exercise_type == 'chord':
        semitones = CHORD_FORMULAS.get(answer)
        if semitones is not None:
            return jsonify({'type': 'chord', 'semitones': semitones, 'root_note': root_note})
    
    elif exercise_type == 'melody':
        pattern = answer.split('-')
        semitones = []
        for degree in pattern:
            s = SCALE_DEGREES.get(degree.strip())
            if s is not None:
                semitones.append(s)
        if semitones:
            return jsonify({'type': 'melody', 'semitones': semitones, 'root_note': root_note})
    
    return jsonify({'error': 'Cannot generate audio for this exercise'}), 400


@bp.route('/ear-training/submit', methods=['POST'])
def submit_ear_training_answer():
    """Submit an ear training answer."""
    data = request.get_json()
    
    exercise_id = data.get('exercise_id')
    user_answer = data.get('answer')
    response_time = data.get('response_time')
    
    cached = _ear_training_cache.get(exercise_id)
    if not cached:
        return jsonify({'error': 'Exercise expired, please try again'}), 400
    
    correct = user_answer == cached['correct_answer']
    
    result = EarTrainingResult(
        exercise_id=0,
        user_answer=user_answer,
        correct=correct,
        response_time_ms=response_time
    )
    db.session.add(result)
    db.session.commit()
    
    if correct:
        update_progress_for_category('theory', duration_minutes=0)
    
    del _ear_training_cache[exercise_id]
    
    return jsonify({
        'correct': correct,
        'correct_answer': cached['correct_answer']
    })
