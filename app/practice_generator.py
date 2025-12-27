"""
Practice session generation logic using dynamic exercise generation.
"""
import random
from datetime import date
from .models import db, PracticeSession, SessionExercise, Progress, DynamicExercise
from .exercise_generator import generate_exercise, generate_practice_session as gen_exercises, EXERCISE_CATEGORIES


def calculate_session_structure(duration):
    """Calculate time allocation for each session phase."""
    structures = {
        15: {'warmup': 3, 'technique': 7, 'musical': 5, 'cooldown': 0},
        30: {'warmup': 5, 'technique': 12, 'musical': 12, 'cooldown': 1},
        45: {'warmup': 5, 'technique': 18, 'musical': 20, 'cooldown': 2},
        60: {'warmup': 8, 'technique': 22, 'musical': 25, 'cooldown': 5},
        90: {'warmup': 10, 'technique': 35, 'musical': 40, 'cooldown': 5},
        120: {'warmup': 15, 'technique': 45, 'musical': 55, 'cooldown': 5}
    }
    return structures.get(duration, structures[30])


def get_weak_categories():
    """Identify categories that need more practice based on progress data."""
    progress_data = Progress.query.all()
    
    if not progress_data:
        return ['scales', 'technique', 'rhythm']
    
    # Sort by skill level (lowest first)
    sorted_progress = sorted(progress_data, key=lambda p: p.skill_level)
    
    # Return bottom 3 categories
    weak = [p.category for p in sorted_progress][:3]
    
    # Ensure we have at least some categories
    for cat in EXERCISE_CATEGORIES:
        if cat not in weak and len(weak) < 3:
            weak.append(cat)
    
    return weak if weak else ['scales', 'technique', 'rhythm']


def generate_practice_session(skill_level, duration_minutes, preferred_genre=None):
    """
    Generate a balanced practice session with dynamically generated exercises.
    """
    # Get session structure
    structure = calculate_session_structure(duration_minutes)
    
    # Create the practice session
    session = PracticeSession(
        session_date=date.today(),
        planned_duration=duration_minutes,
        total_exercises=0
    )
    db.session.add(session)
    db.session.flush()  # Get session ID
    
    exercises_added = []
    order_index = 0
    
    # Get weak categories for focus
    weak_categories = get_weak_categories()
    
    # Phase definitions with category preferences
    phases = [
        ('warmup', structure['warmup'], ['scales', 'technique'], max(1, skill_level - 1)),
        ('technique', structure['technique'], weak_categories + ['technique'], skill_level),
        ('musical', structure['musical'], ['rhythm', 'arpeggios', 'theory'], skill_level),
        ('cooldown', structure['cooldown'], ['scales', 'arpeggios'], max(1, skill_level - 1)),
    ]
    
    for phase_name, phase_duration, categories, difficulty in phases:
        if phase_duration <= 0:
            continue
        
        remaining_time = phase_duration
        
        while remaining_time >= 3:  # Minimum 3 minutes per exercise
            # Pick a random category from phase preferences
            category = random.choice(categories)
            
            # Generate a dynamic exercise
            exercise_data = generate_exercise(category, difficulty)
            
            exercise_time = exercise_data.get('duration', 5)
            if exercise_time > remaining_time:
                exercise_time = remaining_time
            
            # Create a DynamicExercise record
            dynamic_exercise = DynamicExercise(
                title=exercise_data['title'],
                category=exercise_data['category'],
                subcategory=exercise_data.get('subcategory', ''),
                difficulty_level=exercise_data.get('difficulty', difficulty),
                estimated_duration=exercise_time,
                instructions=exercise_data.get('instructions', ''),
                tips=exercise_data.get('tips', ''),
                description=exercise_data.get('description', ''),
                key_signature=exercise_data.get('key', ''),
                tempo_bpm=exercise_data.get('tempo', 80),
                tab_notation=exercise_data.get('tab', ''),
                notes_data=str(exercise_data.get('notes', [])),
            )
            db.session.add(dynamic_exercise)
            db.session.flush()
            
            # Create session exercise link
            session_exercise = SessionExercise(
                session_id=session.id,
                exercise_id=0,  # Not using static exercises
                dynamic_exercise_id=dynamic_exercise.id,
                order_index=order_index,
                planned_duration=exercise_time,
                phase=phase_name
            )
            db.session.add(session_exercise)
            
            exercises_added.append((phase_name, dynamic_exercise))
            order_index += 1
            remaining_time -= exercise_time
    
    # Update total exercises count
    session.total_exercises = order_index
    
    db.session.commit()
    
    return session


def generate_single_exercise(category=None, difficulty=1):
    """Generate a single dynamic exercise for standalone practice."""
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
    
    return dynamic_exercise
