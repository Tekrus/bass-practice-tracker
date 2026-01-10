import random
from ..config.settings import SCALE_FORMULAS, NOTES, BASS_STRINGS
from ..utils.music_theory import note_to_index as get_note_index, index_to_note as get_note_at_index
from .utils import pick_key, pick_tempo, generate_tab, get_fret_for_note

def get_scale_notes(root, scale_type):
    """Get the notes in a scale."""
    root_idx = get_note_index(root)
    formula = SCALE_FORMULAS.get(scale_type, SCALE_FORMULAS['major'])
    use_flats = 'b' in root or root in ['F', 'Bb', 'Eb', 'Ab', 'Db', 'Gb']
    return [get_note_at_index(root_idx + interval, use_flats) for interval in formula]

def get_scale_positions(root, scale_type, position=1):
    """Get fret positions for a scale in a specific position."""
    notes = get_scale_notes(root, scale_type)
    positions = []
    
    # Determine starting fret based on root and position
    root_fret_on_e = get_fret_for_note(4, root)
    if position == 2:
        root_fret_on_e = (root_fret_on_e + 5) % 12
    elif position == 3:
        root_fret_on_e = (root_fret_on_e + 7) % 12
    
    # Map scale notes across strings
    for note in notes:
        # Find the best string/fret combination near the position
        best_string = 4
        best_fret = get_fret_for_note(4, note)
        
        for string_num in [4, 3, 2, 1]:
            fret = get_fret_for_note(string_num, note)
            # Adjust for octaves
            while fret < root_fret_on_e - 3:
                fret += 12
            if root_fret_on_e - 2 <= fret <= root_fret_on_e + 5:
                best_string = string_num
                best_fret = fret
                break
        
        positions.append((best_string, best_fret, note))
    
    return positions

def generate_scale_exercise(difficulty):
    """Generate a scale practice exercise."""
    key = pick_key(difficulty)
    tempo = pick_tempo(difficulty)
    
    # Scale types by difficulty
    if difficulty <= 2:
        scale_types = ['major', 'natural minor', 'major pentatonic', 'minor pentatonic']
    elif difficulty <= 3:
        scale_types = ['major', 'natural minor', 'major pentatonic', 'minor pentatonic', 'blues', 'dorian']
    else:
        scale_types = list(SCALE_FORMULAS.keys())
        scale_types.remove('chromatic')  # Separate exercise for chromatic
    
    scale_type = random.choice(scale_types)
    notes = get_scale_notes(key, scale_type)
    positions = get_scale_positions(key, scale_type)
    
    # Generate tab
    tab_notes = [(pos[0], pos[1]) for pos in positions]
    tab = generate_tab(tab_notes)
    
    # Determine octaves
    octaves = 1 if difficulty <= 2 else 2
    
    # Pattern variations for higher difficulty
    patterns = ['ascending and descending']
    if difficulty >= 3:
        patterns.extend(['in thirds', 'in fourths', 'with sequences'])
    pattern = random.choice(patterns)
    
    instructions = [
        f"Play the {key} {scale_type} scale {pattern}.",
        f"Start at {tempo} BPM with quarter notes.",
        f"Focus on even timing and clean note transitions.",
    ]
    
    if difficulty >= 2:
        instructions.append("Use strict alternate finger picking (index-middle).")
    if difficulty >= 3:
        instructions.append(f"Extend to {octaves} octaves across the neck.")
    if difficulty >= 4:
        instructions.append("Increase tempo by 10 BPM after playing cleanly 3 times.")
    
    tips = [
        "Keep your fretting hand relaxed.",
        f"The {scale_type} scale formula gives it its characteristic sound.",
        "Visualize the scale pattern on the fretboard.",
    ]
    
    return {
        'title': f'{key} {scale_type.title()} Scale',
        'category': 'scales',
        'subcategory': scale_type.replace(' ', '_'),
        'difficulty': difficulty,
        'duration': 3 + difficulty,
        'key': key,
        'tempo': tempo,
        'notes': notes,
        'tab': tab,
        'instructions': '\n'.join(instructions),
        'tips': random.choice(tips),
        'description': f"Practice the {key} {scale_type} scale to build fretboard knowledge and finger dexterity.",
    }

def generate_chromatic_exercise(difficulty):
    """Generate a chromatic scale exercise."""
    tempo = pick_tempo(difficulty)
    
    # Starting position
    start_fret = random.randint(1, 5)
    
    instructions = [
        f"Play the chromatic scale starting at fret {start_fret}.",
        "Use one finger per fret (1-2-3-4).",
        "Move across all four strings.",
        f"Start at {tempo} BPM with quarter notes.",
    ]
    
    if difficulty >= 2:
        instructions.append("Play ascending on one string, then shift to the next.")
    if difficulty >= 3:
        instructions.append("Add descending pattern after reaching the top.")
    if difficulty >= 4:
        instructions.append("Use eighth notes and increase tempo.")
    if difficulty >= 5:
        instructions.append("Add hammer-ons for each group of 4 notes.")
    
    tips = [
        "The chromatic scale includes all 12 notes.",
        "Great for warming up and building finger strength.",
        "Focus on even timing between all notes.",
    ]
    
    return {
        'title': 'Chromatic Scale Exercise',
        'category': 'scales',
        'subcategory': 'chromatic',
        'difficulty': difficulty,
        'duration': 3 + difficulty,
        'tempo': tempo,
        'start_fret': start_fret,
        'instructions': '\n'.join(instructions),
        'tips': random.choice(tips),
        'description': "Practice the chromatic scale for finger coordination and fretboard coverage.",
    }
