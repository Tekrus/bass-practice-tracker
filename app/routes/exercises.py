from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from ..models import db, Exercise, DynamicExercise, Progress
from ..exercise_generator import generate_exercise, EXERCISE_CATEGORIES
from ..utils.database import update_progress_for_category

bp = Blueprint('exercises', __name__)

@bp.route('/exercises')
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


@bp.route('/exercises/<int:exercise_id>')
def exercise_detail(exercise_id):
    """View exercise details."""
    exercise = Exercise.query.get_or_404(exercise_id)
    return render_template('exercise_detail.html', exercise=exercise)


@bp.route('/exercises/dynamic/<int:exercise_id>')
def dynamic_exercise_detail(exercise_id):
    """View dynamically generated exercise details."""
    exercise = DynamicExercise.query.get_or_404(exercise_id)
    return render_template('dynamic_exercise_detail.html', exercise=exercise)


@bp.route('/exercises/generate')
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


@bp.route('/exercises/categories')
def get_exercise_categories():
    """Get available exercise categories."""
    return jsonify({
        'categories': EXERCISE_CATEGORIES
    })


@bp.route('/exercises/complete', methods=['POST'])
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


@bp.route('/exercises/recommended')
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
    return redirect(url_for('exercises.dynamic_exercise_detail', exercise_id=dynamic_exercise.id))
