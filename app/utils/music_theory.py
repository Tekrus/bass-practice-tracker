"""
Common music theory utility functions for the bass practice application.
"""

# Constants needed for utilities (will be move to config later)
NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
NOTES_FLAT = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']

def note_to_index(note):
    """Get the index (0-11) of a note."""
    if note in NOTES:
        return NOTES.index(note)
    if note in NOTES_FLAT:
        return NOTES_FLAT.index(note)
    return 0

def index_to_note(index, use_flats=False):
    """Get note name at given index (0-11), wrapping around."""
    index = index % 12
    return NOTES_FLAT[index] if use_flats else NOTES[index]

def transpose_note(note, semitones, use_flats=None):
    """Transpose a note by a number of semitones."""
    current_idx = note_to_index(note)
    if use_flats is None:
        use_flats = 'b' in note or note in ['F', 'Bb', 'Eb', 'Ab', 'Db', 'Gb']
    return index_to_note(current_idx + semitones, use_flats)

def get_interval_name(semitones):
    """Get the name of an interval based on semitones."""
    intervals = {
        0: 'Perfect Unison',
        1: 'minor 2nd',
        2: 'Major 2nd',
        3: 'minor 3rd',
        4: 'Major 3rd',
        5: 'Perfect 4th',
        6: 'Tritone',
        7: 'Perfect 5th',
        8: 'minor 6th',
        9: 'Major 6th',
        10: 'minor 7th',
        11: 'Major 7th',
        12: 'Octave'
    }
    return intervals.get(semitones % 12 if semitones < 12 else 12, f"{semitones} semitones")

def get_semitones_for_interval(interval_name):
    """Get the number of semitones for a given interval name."""
    intervals = {
        'unison': 0,
        'minor 2nd': 1,
        'major 2nd': 2,
        'minor 3rd': 3,
        'major 3rd': 4,
        'perfect 4th': 5,
        'tritone': 6,
        'perfect 5th': 7,
        'minor 6th': 8,
        'major 6th': 9,
        'minor 7th': 10,
        'major 7th': 11,
        'octave': 12
    }
    return intervals.get(interval_name.lower(), 0)
