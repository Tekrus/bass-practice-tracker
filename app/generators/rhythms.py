import random
from ..config.settings import CHORD_PROGRESSIONS, RHYTHM_PATTERNS
from ..utils.music_theory import note_to_index as get_note_index, index_to_note as get_note_at_index
from .utils import pick_key, pick_tempo

def generate_chord_progression_exercise(difficulty):
    """Generate a chord progression practice exercise."""
    key = pick_key(difficulty)
    tempo = pick_tempo(difficulty)
    
    # Progressions by difficulty
    if difficulty <= 2:
        prog_names = ['I-IV-V', 'I-IV', 'i-iv-v']
    elif difficulty <= 3:
        prog_names = ['I-IV-V', 'I-V-vi-IV', 'I-vi-IV-V', 'I-IV', '12-bar blues']
    else:
        prog_names = list(CHORD_PROGRESSIONS.keys())
    
    prog_name = random.choice(prog_names)
    progression = CHORD_PROGRESSIONS[prog_name]
    
    # Calculate actual chords in the key
    key_idx = get_note_index(key)
    use_flats = 'b' in key or key in ['F', 'Bb', 'Eb', 'Ab', 'Db', 'Gb']
    
    chords = []
    for offset, chord_type in progression:
        chord_root = get_note_at_index(key_idx + offset, use_flats)
        chords.append(f"{chord_root} {chord_type}")
    
    # Bass line approach
    approaches = ['root notes only']
    if difficulty >= 2:
        approaches.append('root and fifth')
    if difficulty >= 3:
        approaches.extend(['walking quarters', 'arpeggiated'])
    if difficulty >= 4:
        approaches.append('chromatic approaches')
    
    approach = random.choice(approaches)
    
    instructions = [
        f"Play the {prog_name} progression in the key of {key}.",
        f"Chords: {' | '.join(chords[:4])}{'...' if len(chords) > 4 else ''}",
        f"Use {approach} at {tempo} BPM.",
    ]
    
    if difficulty >= 2:
        instructions.append("Focus on smooth chord transitions.")
    if difficulty >= 3:
        instructions.append("Add fills on the last beat of each chord.")
    if difficulty >= 4:
        instructions.append("Experiment with inversions to minimize hand movement.")
    
    tips = [
        f"The {prog_name} progression is common in many genres.",
        "Listen for how each chord resolves to the next.",
        "Root notes on beat 1 establish the harmony clearly.",
    ]
    
    return {
        'title': f'{prog_name} Progression in {key}',
        'category': 'rhythm',
        'subcategory': 'chord_progressions',
        'difficulty': difficulty,
        'duration': 4 + difficulty,
        'key': key,
        'tempo': tempo,
        'chords': chords,
        'progression_name': prog_name,
        'instructions': '\n'.join(instructions),
        'tips': random.choice(tips),
        'description': f"Practice the {prog_name} chord progression to build harmonic awareness.",
    }

def generate_rhythm_exercise(difficulty):
    """Generate a rhythm pattern exercise."""
    key = pick_key(difficulty)
    tempo = pick_tempo(difficulty)
    
    # Rhythm patterns by difficulty
    if difficulty <= 2:
        patterns = ['quarter notes', 'eighth notes', 'half notes']
    elif difficulty <= 3:
        patterns = ['quarter notes', 'eighth notes', 'eighth note groove', 'dotted quarter']
    else:
        patterns = list(RHYTHM_PATTERNS.keys())
    
    pattern_name = random.choice(patterns)
    pattern = RHYTHM_PATTERNS[pattern_name]
    
    # Pick a simple chord or single note
    note = key  # Root note
    
    instructions = [
        f"Play {pattern_name} on the note {note}.",
        f"Start at {tempo} BPM with a metronome.",
        "Focus on locking in with the click.",
    ]
    
    if difficulty >= 2:
        instructions.append("Accent the downbeats (1 and 3 in 4/4).")
    if difficulty >= 3:
        instructions.append("Add ghost notes between main notes.")
    if difficulty >= 4:
        instructions.append("Shift the accent to create different feels.")
    if difficulty >= 5:
        instructions.append("Try playing slightly behind the beat for a laid-back feel.")
    
    tips = [
        "Rhythm is the foundation of bass playing.",
        "A steady groove is more important than complex notes.",
        "Practice with a metronome to develop internal timing.",
    ]
    
    return {
        'title': f'{pattern_name.title()} Rhythm Exercise',
        'category': 'rhythm',
        'subcategory': pattern_name.replace(' ', '_'),
        'difficulty': difficulty,
        'duration': 3 + difficulty,
        'key': key,
        'tempo': tempo,
        'pattern': pattern,
        'pattern_name': pattern_name,
        'instructions': '\n'.join(instructions),
        'tips': random.choice(tips),
        'description': f"Practice {pattern_name} to develop solid timing and groove.",
    }
