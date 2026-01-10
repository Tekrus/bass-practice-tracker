import random
from ..config.settings import NOTES, TEMPO_RANGES, BASS_STRINGS
from ..utils.music_theory import note_to_index as get_note_index

# Keys by difficulty (natural keys first, then sharps/flats)
KEYS_BY_DIFFICULTY = {
    1: ['C', 'G', 'A', 'E', 'D'],
    2: ['C', 'G', 'A', 'E', 'D', 'F', 'B'],
    3: NOTES[:7],  # Natural notes
    4: NOTES[:10],
    5: NOTES,
}

def pick_key(difficulty):
    """Pick a random key appropriate for the difficulty level."""
    keys = KEYS_BY_DIFFICULTY.get(difficulty, NOTES)
    return random.choice(keys)

def pick_tempo(difficulty):
    """Pick a random tempo appropriate for the difficulty level."""
    min_tempo, max_tempo = TEMPO_RANGES.get(difficulty, (60, 100))
    # Round to nearest 5
    return round(random.randint(min_tempo, max_tempo) / 5) * 5

def get_fret_for_note(string_num, note):
    """Get the fret number for a note on a specific string (within first 12 frets)."""
    open_note_idx = BASS_STRINGS[string_num]
    target_idx = get_note_index(note)
    fret = (target_idx - open_note_idx) % 12
    return fret

def generate_tab(notes_per_string):
    """Generate tab notation for a sequence of notes."""
    lines = {1: 'G|', 2: 'D|', 3: 'A|', 4: 'E|'}
    
    for string_num, fret in notes_per_string:
        for s in [1, 2, 3, 4]:
            if s == string_num:
                lines[s] += f'{fret:2d}-'
            else:
                lines[s] += '---'
    
    for s in [1, 2, 3, 4]:
        lines[s] += '|'
    
    return '\n'.join([lines[1], lines[2], lines[3], lines[4]])
