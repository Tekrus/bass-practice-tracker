import random
from .scales import generate_scale_exercise, generate_chromatic_exercise, get_scale_notes
from .arpeggios import generate_arpeggio_exercise, get_arpeggio_notes
from .rhythms import generate_chord_progression_exercise, generate_rhythm_exercise

# These are specific to exercise_generator.py logic but I'll move them to technique.py if I were to split it further.
# For now I'll include them in the generator map.

EXERCISE_GENERATORS = {
    'scales': [generate_scale_exercise, generate_chromatic_exercise],
    'arpeggios': [generate_arpeggio_exercise],
    'rhythm': [generate_chord_progression_exercise, generate_rhythm_exercise],
    'technique': [], # To be filled by technique.py
    'theory': [], # To be filled by theory.py
}

def generate_exercise(category=None, difficulty=1):
    """Generate a random exercise for the given category."""
    from .technique import generate_technique_exercise, generate_finger_exercise
    from .theory import generate_interval_exercise
    
    # Update generators map if empty
    if not EXERCISE_GENERATORS['technique']:
        EXERCISE_GENERATORS['technique'] = [generate_technique_exercise, generate_finger_exercise]
    if not EXERCISE_GENERATORS['theory']:
        EXERCISE_GENERATORS['theory'] = [generate_interval_exercise]
        
    categories = list(EXERCISE_GENERATORS.keys())
    
    if category is None or category not in EXERCISE_GENERATORS:
        category = random.choice(categories)
    
    generators = EXERCISE_GENERATORS[category]
    generator = random.choice(generators)
    
    return generator(difficulty)
