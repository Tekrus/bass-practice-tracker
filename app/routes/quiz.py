from flask import Blueprint, render_template, request, jsonify
from ..models import db, QuizResult
from ..quiz_generator import generate_quiz, QUIZ_CATEGORIES

bp = Blueprint('quiz', __name__)

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
    
    if accuracy >= 0.8:
        return min(5, len(recent_results) // 2 + 1)
    elif accuracy <= 0.4:
        return max(1, len(recent_results) // 3)
    return max(1, min(5, int(len(recent_results) / 2)))


@bp.route('/quiz')
def quiz():
    """Quiz main page."""
    quiz_category = request.args.get('type', 'fretboard')
    
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
    
    total_attempts = QuizResult.query.count()
    correct_attempts = QuizResult.query.filter_by(correct=True).count()
    overall_accuracy = (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0
    
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


@bp.route('/quiz/question')
def get_quiz_question():
    """Generate a dynamic quiz question."""
    import uuid
    
    quiz_category = request.args.get('type', 'fretboard')
    difficulty = calculate_quiz_difficulty(quiz_category)
    
    question = generate_quiz(quiz_category, difficulty)
    
    question_id = str(uuid.uuid4())
    
    _quiz_cache[question_id] = {
        'correct_answer': question['correct_answer'],
        'explanation': question.get('explanation', ''),
        'quiz_type': quiz_category,
    }
    
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


@bp.route('/quiz/submit', methods=['POST'])
def submit_quiz_answer():
    """Submit a quiz answer."""
    data = request.get_json()
    
    question_id = data.get('quiz_id')
    user_answer = data.get('answer')
    response_time = data.get('response_time')
    
    cached = _quiz_cache.get(question_id)
    if not cached:
        return jsonify({'error': 'Question expired, please try again'}), 400
    
    correct = user_answer == cached['correct_answer']
    
    result = QuizResult(
        quiz_id=0,
        quiz_type=cached['quiz_type'],
        user_answer=user_answer,
        correct=correct,
        response_time_ms=response_time
    )
    db.session.add(result)
    db.session.commit()
    
    del _quiz_cache[question_id]
    
    return jsonify({
        'correct': correct,
        'correct_answer': cached['correct_answer'],
        'explanation': cached['explanation']
    })
