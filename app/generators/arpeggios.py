import random
from ..config.settings import ARPEGGIO_FORMULAS
from ..utils.music_theory import note_to_index as get_note_index, index_to_note as get_note_at_index
from .utils import pick_key, pick_tempo, generate_tab, get_fret_for_note

def get_arpeggio_notes(root, arpeggio_type):
    """Get the notes in an arpeggio."""
    root_idx = get_note_index(root)
    formula = ARPEGGIO_FORMULAS.get(arpeggio_type, ARPEGGIO_FORMULAS['major triad'])
    use_flats = 'b' in root or root in ['F', 'Bb', 'Eb', 'Ab', 'Db', 'Gb']
    return [get_note_at_index(root_idx + interval, use_flats) for interval in formula]

def generate_arpeggio_exercise(difficulty):
    """Generate an arpeggio practice exercise."""
    key = pick_key(difficulty)
    tempo = pick_tempo(difficulty)
    
    # Arpeggio types by difficulty
    if difficulty <= 2:
        arp_types = ['major triad', 'minor triad']
    elif difficulty <= 3:
        arp_types = ['major triad', 'minor triad', 'diminished triad', 'major 7th', 'minor 7th', 'dominant 7th']
    else:
        arp_types = list(ARPEGGIO_FORMULAS.keys())
    
    arp_type = random.choice(arp_types)
    notes = get_arpeggio_notes(key, arp_type)
    
    # Generate simple tab (root position)
    tab_notes = []
    for note in notes:
        string = random.choice([3, 4])  # Prefer lower strings for bass
        fret = get_fret_for_note(string, note)
        tab_notes.append((string, fret))
    tab = generate_tab(tab_notes)
    
    # Inversions for higher difficulty
    inversions = ['root position']
    if difficulty >= 3:
        inversions.extend(['1st inversion', '2nd inversion'])
    if difficulty >= 4 and len(notes) >= 4:
        inversions.append('3rd inversion')
    
    inversion = random.choice(inversions)
    
    instructions = [
        f"Play the {key} {arp_type} arpeggio in {inversion}.",
        f"Start at {tempo} BPM.",
        "Play each note cleanly and let it ring into the next.",
    ]
    
    if difficulty >= 2:
        instructions.append("Practice both ascending and descending.")
    if difficulty >= 3:
        instructions.append("Connect inversions smoothly across the fretboard.")
    if difficulty >= 4:
        instructions.append("Try playing over a backing track in the same key.")
    
    tips = [
        f"A {arp_type} is built from the chord tones: {', '.join(notes)}.",
        "Arpeggios outline the harmony - essential for bass players!",
        "Visualize the chord shape as you play the arpeggio.",
    ]
    
    return {
        'title': f'{key} {arp_type.title()} Arpeggio',
        'category': 'arpeggios',
        'subcategory': arp_type.replace(' ', '_'),
        'difficulty': difficulty,
        'duration': 3 + difficulty,
        'key': key,
        'tempo': tempo,
        'notes': notes,
        'tab': tab,
        'instructions': '\n'.join(instructions),
        'tips': random.choice(tips),
        'description': f"Practice the {key} {arp_type} arpeggio to master chord tones.",
    }
