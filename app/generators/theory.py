import random
from ..utils.music_theory import note_to_index as get_note_index, index_to_note as get_note_at_index
from .utils import pick_key, pick_tempo, get_fret_for_note

def generate_interval_exercise(difficulty):
    """Generate an interval training exercise."""
    key = pick_key(difficulty)
    tempo = pick_tempo(difficulty)
    
    # Intervals by difficulty
    if difficulty <= 2:
        intervals = [(5, 'Perfect 4th'), (7, 'Perfect 5th'), (12, 'Octave')]
    elif difficulty <= 3:
        intervals = [(3, 'minor 3rd'), (4, 'Major 3rd'), (5, 'Perfect 4th'), 
                    (7, 'Perfect 5th'), (12, 'Octave')]
    else:
        intervals = [(2, 'Major 2nd'), (3, 'minor 3rd'), (4, 'Major 3rd'), 
                    (5, 'Perfect 4th'), (6, 'Tritone'), (7, 'Perfect 5th'),
                    (8, 'minor 6th'), (9, 'Major 6th'), (10, 'minor 7th'),
                    (11, 'Major 7th'), (12, 'Octave')]
    
    semitones, interval_name = random.choice(intervals)
    root_idx = get_note_index(key)
    second_note = get_note_at_index(root_idx + semitones)
    
    instructions = [
        f"Play the interval of a {interval_name} starting from {key}.",
        f"The two notes are {key} and {second_note}.",
        f"On the E string: fret {get_fret_for_note(4, key)} to fret {get_fret_for_note(4, second_note)}.",
        f"Play at {tempo} BPM, holding each note for 2 beats.",
    ]
    
    if difficulty >= 2:
        instructions.append("Sing the interval as you play it.")
    if difficulty >= 3:
        instructions.append("Practice the interval on all four strings.")
    if difficulty >= 4:
        instructions.append("Create a bass line using primarily this interval.")
    
    tips = [
        f"A {interval_name} is {semitones} frets apart.",
        "Learning intervals helps you navigate the fretboard by ear.",
        f"The {interval_name} has a distinctive sound - try to memorize it.",
    ]
    
    return {
        'title': f'{interval_name} Interval Exercise',
        'category': 'theory',
        'subcategory': 'intervals',
        'difficulty': difficulty,
        'duration': 3 + difficulty,
        'key': key,
        'tempo': tempo,
        'interval': interval_name,
        'semitones': semitones,
        'notes': [key, second_note],
        'instructions': '\n'.join(instructions),
        'tips': random.choice(tips),
        'description': f"Practice the {interval_name} interval to develop your ear and fretboard knowledge.",
    }
