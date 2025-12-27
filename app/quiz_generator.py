"""
Dynamic quiz generator for bass guitar practice.
Generates questions algorithmically based on music theory.
"""
import random
import json

# =============================================================================
# MUSIC THEORY CONSTANTS
# =============================================================================

NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
NOTES_FLAT = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']

# Enharmonic equivalents
ENHARMONIC = {
    'C#': 'Db', 'Db': 'C#',
    'D#': 'Eb', 'Eb': 'D#',
    'F#': 'Gb', 'Gb': 'F#',
    'G#': 'Ab', 'Ab': 'G#',
    'A#': 'Bb', 'Bb': 'A#',
}

# Bass string open notes (string number -> note index in NOTES)
BASS_STRINGS = {
    1: 7,   # G string - index 7
    2: 2,   # D string - index 2
    3: 9,   # A string - index 9
    4: 4,   # E string - index 4
}
STRING_NAMES = {1: 'G', 2: 'D', 3: 'A', 4: 'E'}

# Intervals (semitones -> name)
INTERVALS = {
    0: 'Unison',
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
    12: 'Octave',
}

# Chord formulas (intervals from root in semitones)
CHORD_FORMULAS = {
    'major': [0, 4, 7],
    'minor': [0, 3, 7],
    'diminished': [0, 3, 6],
    'augmented': [0, 4, 8],
    'sus2': [0, 2, 7],
    'sus4': [0, 5, 7],
    'major 7th': [0, 4, 7, 11],
    'minor 7th': [0, 3, 7, 10],
    'dominant 7th': [0, 4, 7, 10],
    'diminished 7th': [0, 3, 6, 9],
    'half-diminished 7th': [0, 3, 6, 10],
    'minor-major 7th': [0, 3, 7, 11],
    'augmented 7th': [0, 4, 8, 10],
    'major 9th': [0, 4, 7, 11, 14],
    'minor 9th': [0, 3, 7, 10, 14],
    'dominant 9th': [0, 4, 7, 10, 14],
}

# Scale formulas (intervals from root in semitones)
SCALE_FORMULAS = {
    'major': [0, 2, 4, 5, 7, 9, 11],
    'natural minor': [0, 2, 3, 5, 7, 8, 10],
    'harmonic minor': [0, 2, 3, 5, 7, 8, 11],
    'melodic minor': [0, 2, 3, 5, 7, 9, 11],
    'major pentatonic': [0, 2, 4, 7, 9],
    'minor pentatonic': [0, 3, 5, 7, 10],
    'blues': [0, 3, 5, 6, 7, 10],
    'dorian': [0, 2, 3, 5, 7, 9, 10],
    'phrygian': [0, 1, 3, 5, 7, 8, 10],
    'lydian': [0, 2, 4, 6, 7, 9, 11],
    'mixolydian': [0, 2, 4, 5, 7, 9, 10],
    'locrian': [0, 1, 3, 5, 6, 8, 10],
}

# Key signatures (number of sharps positive, flats negative)
KEY_SIGNATURES = {
    'C': 0, 'G': 1, 'D': 2, 'A': 3, 'E': 4, 'B': 5, 'F#': 6,
    'F': -1, 'Bb': -2, 'Eb': -3, 'Ab': -4, 'Db': -5, 'Gb': -6,
}

# Circle of fifths order
CIRCLE_OF_FIFTHS = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#', 'Ab', 'Eb', 'Bb', 'F']


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_note_at_index(index, use_flats=False):
    """Get note name at given index (0-11), wrapping around."""
    index = index % 12
    return NOTES_FLAT[index] if use_flats else NOTES[index]


def get_note_index(note):
    """Get the index (0-11) of a note."""
    if note in NOTES:
        return NOTES.index(note)
    if note in NOTES_FLAT:
        return NOTES_FLAT.index(note)
    return 0


def get_chord_notes(root, chord_type):
    """Get the notes in a chord."""
    root_idx = get_note_index(root)
    formula = CHORD_FORMULAS.get(chord_type, [0, 4, 7])
    use_flats = 'b' in root or root in ['F', 'Bb', 'Eb', 'Ab', 'Db', 'Gb']
    return [get_note_at_index(root_idx + interval, use_flats) for interval in formula]


def get_scale_notes(root, scale_type):
    """Get the notes in a scale."""
    root_idx = get_note_index(root)
    formula = SCALE_FORMULAS.get(scale_type, [0, 2, 4, 5, 7, 9, 11])
    use_flats = 'b' in root or root in ['F', 'Bb', 'Eb', 'Ab', 'Db', 'Gb']
    return [get_note_at_index(root_idx + interval, use_flats) for interval in formula]


def get_note_on_fretboard(string_num, fret):
    """Get the note at a specific fretboard position."""
    open_note_idx = BASS_STRINGS[string_num]
    return get_note_at_index(open_note_idx + fret)


def get_random_wrong_notes(correct_note, count=3):
    """Generate plausible wrong note options."""
    correct_idx = get_note_index(correct_note)
    wrong_notes = []
    
    # Prioritize nearby notes (common mistakes)
    offsets = [-2, -1, 1, 2, -3, 3, 5, 7]
    random.shuffle(offsets)
    
    for offset in offsets:
        wrong = get_note_at_index(correct_idx + offset)
        if wrong != correct_note and wrong not in wrong_notes:
            wrong_notes.append(wrong)
            if len(wrong_notes) >= count:
                break
    
    return wrong_notes


def shuffle_options(correct, wrong_options):
    """Shuffle correct answer with wrong options."""
    options = [correct] + wrong_options
    random.shuffle(options)
    return options


# =============================================================================
# QUIZ GENERATORS
# =============================================================================

def generate_fretboard_quiz(difficulty):
    """Generate a fretboard note identification question."""
    # Higher difficulty = more frets, sharps/flats
    max_fret = min(5 + difficulty * 2, 12)
    
    string_num = random.randint(1, 4)
    fret = random.randint(0, max_fret)
    
    correct_note = get_note_on_fretboard(string_num, fret)
    wrong_notes = get_random_wrong_notes(correct_note)
    
    return {
        'type': 'fretboard',
        'title': 'Identify the Note',
        'question': f'What note is at fret {fret} on the {STRING_NAMES[string_num]} string?',
        'correct_answer': correct_note,
        'options': json.dumps(shuffle_options(correct_note, wrong_notes)),
        'explanation': f'The {STRING_NAMES[string_num]} string open is {STRING_NAMES[string_num]}. '
                      f'Adding {fret} frets gives you {correct_note}.',
        'difficulty': difficulty,
        'string_number': string_num,
        'fret_number': fret,
    }


def generate_chord_tones_quiz(difficulty):
    """Generate a 'which notes are in this chord' question."""
    # Select chord complexity based on difficulty
    if difficulty <= 2:
        chord_types = ['major', 'minor']
    elif difficulty <= 3:
        chord_types = ['major', 'minor', 'diminished', 'augmented', 'sus2', 'sus4']
    else:
        chord_types = list(CHORD_FORMULAS.keys())
    
    chord_type = random.choice(chord_types)
    root = random.choice(NOTES[:7] if difficulty <= 2 else NOTES)  # Natural notes for easier difficulty
    
    correct_notes = get_chord_notes(root, chord_type)
    correct_answer = ' '.join(correct_notes)
    
    # Generate wrong options with plausible mistakes
    wrong_options = []
    
    # Wrong option 1: One note off
    wrong1 = correct_notes.copy()
    idx_to_change = random.randint(1, len(wrong1) - 1)  # Don't change root
    wrong1[idx_to_change] = get_note_at_index(get_note_index(wrong1[idx_to_change]) + random.choice([-1, 1]))
    wrong_options.append(' '.join(wrong1))
    
    # Wrong option 2: Different chord type
    other_types = [t for t in chord_types if t != chord_type]
    if other_types:
        other_type = random.choice(other_types)
        wrong_options.append(' '.join(get_chord_notes(root, other_type)))
    
    # Wrong option 3: Wrong root
    wrong_root = get_note_at_index(get_note_index(root) + random.choice([1, 2]))
    wrong_options.append(' '.join(get_chord_notes(wrong_root, chord_type)))
    
    # Ensure we have 3 unique wrong options
    wrong_options = list(set(wrong_options))[:3]
    while len(wrong_options) < 3:
        wrong = correct_notes.copy()
        random.shuffle(wrong)
        wrong_str = ' '.join(wrong)
        if wrong_str != correct_answer and wrong_str not in wrong_options:
            wrong_options.append(wrong_str)
    
    chord_name = f'{root} {chord_type}'
    
    return {
        'type': 'chord_tones',
        'title': 'Chord Tones',
        'question': f'Which notes are in a {chord_name} chord?',
        'correct_answer': correct_answer,
        'options': json.dumps(shuffle_options(correct_answer, wrong_options[:3])),
        'explanation': f'{chord_name} contains the notes {correct_answer}. '
                      f'Formula: {CHORD_FORMULAS[chord_type]}',
        'difficulty': difficulty,
    }


def generate_interval_quiz(difficulty):
    """Generate an interval identification question."""
    # Limit intervals based on difficulty
    if difficulty <= 2:
        max_interval = 7  # Up to Perfect 5th
    elif difficulty <= 3:
        max_interval = 10
    else:
        max_interval = 12
    
    semitones = random.randint(1, max_interval)
    correct_answer = INTERVALS[semitones]
    
    # Wrong options: nearby intervals
    wrong_options = []
    for offset in [-2, -1, 1, 2]:
        wrong_semitones = semitones + offset
        if 0 < wrong_semitones <= 12 and wrong_semitones != semitones:
            wrong_options.append(INTERVALS[wrong_semitones])
    
    wrong_options = list(set(wrong_options))[:3]
    
    return {
        'type': 'interval',
        'title': 'Interval Knowledge',
        'question': f'What interval is {semitones} semitone{"s" if semitones != 1 else ""} (frets)?',
        'correct_answer': correct_answer,
        'options': json.dumps(shuffle_options(correct_answer, wrong_options)),
        'explanation': f'{semitones} semitones = {correct_answer}.',
        'difficulty': difficulty,
    }


def generate_interval_semitones_quiz(difficulty):
    """Generate a 'how many semitones in this interval' question."""
    if difficulty <= 2:
        intervals_subset = {k: v for k, v in INTERVALS.items() if k <= 7}
    else:
        intervals_subset = INTERVALS
    
    semitones = random.choice(list(intervals_subset.keys()))
    if semitones == 0:
        semitones = random.randint(1, 7)
    
    interval_name = INTERVALS[semitones]
    correct_answer = str(semitones)
    
    # Wrong options
    wrong_options = []
    for offset in [-2, -1, 1, 2]:
        wrong = semitones + offset
        if 1 <= wrong <= 12 and wrong != semitones:
            wrong_options.append(str(wrong))
    
    return {
        'type': 'interval_semitones',
        'title': 'Interval Distance',
        'question': f'How many semitones (frets) are in a {interval_name}?',
        'correct_answer': correct_answer,
        'options': json.dumps(shuffle_options(correct_answer, wrong_options[:3])),
        'explanation': f'A {interval_name} is {semitones} semitones (frets).',
        'difficulty': difficulty,
    }


def generate_scale_notes_quiz(difficulty):
    """Generate a scale notes question."""
    if difficulty <= 2:
        scale_types = ['major', 'natural minor', 'major pentatonic', 'minor pentatonic']
    elif difficulty <= 3:
        scale_types = ['major', 'natural minor', 'major pentatonic', 'minor pentatonic', 'blues', 'dorian']
    else:
        scale_types = list(SCALE_FORMULAS.keys())
    
    scale_type = random.choice(scale_types)
    root = random.choice(NOTES[:7] if difficulty <= 2 else NOTES)
    
    correct_notes = get_scale_notes(root, scale_type)
    correct_answer = ' '.join(correct_notes)
    
    # Wrong options
    wrong_options = []
    
    # Different scale type
    other_types = [t for t in scale_types if t != scale_type]
    if other_types:
        wrong_options.append(' '.join(get_scale_notes(root, random.choice(other_types))))
    
    # One note wrong
    wrong1 = correct_notes.copy()
    idx = random.randint(1, len(wrong1) - 1)
    wrong1[idx] = get_note_at_index(get_note_index(wrong1[idx]) + 1)
    wrong_options.append(' '.join(wrong1))
    
    # Wrong root
    wrong_options.append(' '.join(get_scale_notes(get_note_at_index(get_note_index(root) + 1), scale_type)))
    
    wrong_options = list(set(wrong_options))[:3]
    
    return {
        'type': 'scale_notes',
        'title': 'Scale Notes',
        'question': f'Which notes are in the {root} {scale_type} scale?',
        'correct_answer': correct_answer,
        'options': json.dumps(shuffle_options(correct_answer, wrong_options)),
        'explanation': f'The {root} {scale_type} scale contains: {correct_answer}.',
        'difficulty': difficulty,
    }


def generate_key_signature_quiz(difficulty):
    """Generate a key signature question."""
    keys = list(KEY_SIGNATURES.keys())
    if difficulty <= 2:
        keys = ['C', 'G', 'D', 'F', 'Bb']  # Common keys
    
    key = random.choice(keys)
    sig = KEY_SIGNATURES[key]
    
    if sig == 0:
        correct_answer = 'No sharps or flats'
    elif sig > 0:
        correct_answer = f'{sig} sharp{"s" if sig != 1 else ""}'
    else:
        correct_answer = f'{abs(sig)} flat{"s" if abs(sig) != 1 else ""}'
    
    # Generate wrong options
    wrong_options = []
    for offset in [-2, -1, 1, 2]:
        wrong_sig = sig + offset
        if wrong_sig == 0:
            wrong_options.append('No sharps or flats')
        elif wrong_sig > 0:
            wrong_options.append(f'{wrong_sig} sharp{"s" if wrong_sig != 1 else ""}')
        else:
            wrong_options.append(f'{abs(wrong_sig)} flat{"s" if abs(wrong_sig) != 1 else ""}')
    
    wrong_options = [w for w in wrong_options if w != correct_answer][:3]
    
    return {
        'type': 'key_signature',
        'title': 'Key Signatures',
        'question': f'How many sharps or flats are in the key of {key} major?',
        'correct_answer': correct_answer,
        'options': json.dumps(shuffle_options(correct_answer, wrong_options)),
        'explanation': f'{key} major has {correct_answer.lower()}.',
        'difficulty': difficulty,
    }


def generate_relative_minor_quiz(difficulty):
    """Generate a relative minor question."""
    major_keys = ['C', 'G', 'D', 'A', 'E', 'F', 'Bb', 'Eb']
    if difficulty <= 2:
        major_keys = ['C', 'G', 'D', 'F']
    
    major_key = random.choice(major_keys)
    major_idx = get_note_index(major_key)
    
    # Relative minor is 3 semitones below (or 9 above)
    minor_idx = (major_idx - 3) % 12
    correct_answer = get_note_at_index(minor_idx) + ' minor'
    
    # Wrong options
    wrong_options = []
    for offset in [-2, -1, 1, 2, 4]:
        wrong_idx = (minor_idx + offset) % 12
        wrong = get_note_at_index(wrong_idx) + ' minor'
        if wrong != correct_answer:
            wrong_options.append(wrong)
    
    return {
        'type': 'relative_minor',
        'title': 'Relative Minor',
        'question': f'What is the relative minor of {major_key} major?',
        'correct_answer': correct_answer,
        'options': json.dumps(shuffle_options(correct_answer, wrong_options[:3])),
        'explanation': f'The relative minor is 3 semitones below the major key. '
                      f'{major_key} major\'s relative minor is {correct_answer}.',
        'difficulty': difficulty,
    }


def generate_circle_of_fifths_quiz(difficulty):
    """Generate a circle of fifths question."""
    direction = random.choice(['clockwise', 'counter-clockwise'])
    start_key = random.choice(CIRCLE_OF_FIFTHS[:7])  # Natural keys
    
    start_idx = CIRCLE_OF_FIFTHS.index(start_key)
    
    if direction == 'clockwise':
        next_idx = (start_idx + 1) % 12
        question = f'Going clockwise on the circle of fifths from {start_key}, what is the next key?'
    else:
        next_idx = (start_idx - 1) % 12
        question = f'Going counter-clockwise (circle of 4ths) from {start_key}, what is the next key?'
    
    correct_answer = CIRCLE_OF_FIFTHS[next_idx]
    
    # Wrong options from nearby positions
    wrong_options = []
    for offset in [-2, 2, 3, -3]:
        wrong_idx = (next_idx + offset) % 12
        wrong = CIRCLE_OF_FIFTHS[wrong_idx]
        if wrong != correct_answer:
            wrong_options.append(wrong)
    
    return {
        'type': 'circle_of_fifths',
        'title': 'Circle of Fifths',
        'question': question,
        'correct_answer': correct_answer,
        'options': json.dumps(shuffle_options(correct_answer, wrong_options[:3])),
        'explanation': f'The circle of fifths goes: C-G-D-A-E-B-F#... (clockwise adds sharps). '
                      f'Counter-clockwise: C-F-Bb-Eb... (adds flats).',
        'difficulty': difficulty,
    }


def generate_chord_formula_quiz(difficulty):
    """Generate a chord formula question."""
    if difficulty <= 2:
        chord_types = ['major', 'minor', 'diminished']
    elif difficulty <= 3:
        chord_types = ['major', 'minor', 'diminished', 'augmented', 'dominant 7th', 'major 7th', 'minor 7th']
    else:
        chord_types = list(CHORD_FORMULAS.keys())
    
    chord_type = random.choice(chord_types)
    formula = CHORD_FORMULAS[chord_type]
    
    # Convert to interval notation
    interval_names = {
        0: '1', 2: '2', 3: 'b3', 4: '3', 5: '4', 6: 'b5', 7: '5',
        8: '#5', 9: '6', 10: 'b7', 11: '7', 14: '9'
    }
    correct_answer = '-'.join([interval_names.get(i, str(i)) for i in formula])
    
    # Wrong options
    wrong_options = []
    for other_type in chord_types:
        if other_type != chord_type:
            other_formula = CHORD_FORMULAS[other_type]
            wrong = '-'.join([interval_names.get(i, str(i)) for i in other_formula])
            if wrong != correct_answer:
                wrong_options.append(wrong)
    
    return {
        'type': 'chord_formula',
        'title': 'Chord Formulas',
        'question': f'What is the formula for a {chord_type} chord?',
        'correct_answer': correct_answer,
        'options': json.dumps(shuffle_options(correct_answer, wrong_options[:3])),
        'explanation': f'A {chord_type} chord has the formula: {correct_answer}.',
        'difficulty': difficulty,
    }


def generate_note_to_fret_quiz(difficulty):
    """Generate a 'find this note on this string' question."""
    string_num = random.randint(1, 4)
    target_note = random.choice(NOTES[:7] if difficulty <= 2 else NOTES)
    
    # Find the fret for this note on this string
    open_note_idx = BASS_STRINGS[string_num]
    target_idx = get_note_index(target_note)
    fret = (target_idx - open_note_idx) % 12
    
    correct_answer = str(fret)
    
    # Wrong options
    wrong_options = [str((fret + offset) % 12) for offset in [-2, -1, 1, 2]]
    wrong_options = [w for w in wrong_options if w != correct_answer][:3]
    
    return {
        'type': 'note_to_fret',
        'title': 'Find the Note',
        'question': f'At which fret would you find {target_note} on the {STRING_NAMES[string_num]} string?',
        'correct_answer': correct_answer,
        'options': json.dumps(shuffle_options(correct_answer, wrong_options)),
        'explanation': f'{target_note} is at fret {fret} on the {STRING_NAMES[string_num]} string.',
        'difficulty': difficulty,
        'string_number': string_num,
    }


def generate_rhythm_quiz(difficulty):
    """Generate rhythm/note value questions."""
    questions = [
        {
            'question': 'How many eighth notes fit in one measure of 4/4 time?',
            'correct': '8',
            'wrong': ['4', '6', '16'],
            'explanation': '4/4 has 4 quarter notes. Each quarter = 2 eighths. 4 x 2 = 8.',
        },
        {
            'question': 'How many sixteenth notes equal one quarter note?',
            'correct': '4',
            'wrong': ['2', '8', '16'],
            'explanation': 'One quarter = 2 eighths = 4 sixteenths.',
        },
        {
            'question': 'In 4/4 time, how many beats does a half note get?',
            'correct': '2',
            'wrong': ['1', '4', '3'],
            'explanation': 'A half note is half of a whole note (4 beats), so 2 beats.',
        },
        {
            'question': 'What does a dot after a note do?',
            'correct': 'Adds half the note value',
            'wrong': ['Doubles the note value', 'Makes it staccato', 'Adds one beat'],
            'explanation': 'A dot adds half the original value. A dotted half = 2 + 1 = 3 beats.',
        },
        {
            'question': 'What is a triplet?',
            'correct': '3 notes in the space of 2',
            'wrong': ['2 notes in the space of 3', '3 notes in the space of 4', '4 notes in the space of 3'],
            'explanation': 'A triplet divides a beat into 3 equal parts instead of the usual 2.',
        },
        {
            'question': 'In 6/8 time, how many eighth notes per measure?',
            'correct': '6',
            'wrong': ['8', '4', '3'],
            'explanation': '6/8 means 6 eighth notes per measure, usually grouped as 2 groups of 3.',
        },
    ]
    
    q = random.choice(questions)
    return {
        'type': 'rhythm',
        'title': 'Rhythm & Time',
        'question': q['question'],
        'correct_answer': q['correct'],
        'options': json.dumps(shuffle_options(q['correct'], q['wrong'])),
        'explanation': q['explanation'],
        'difficulty': difficulty,
    }


def generate_technique_quiz(difficulty):
    """Generate bass technique questions."""
    questions = [
        {
            'question': 'Where should you press the string relative to the fret for clean tone?',
            'correct': 'Just behind the fret',
            'wrong': ['On top of the fret', 'In the middle of the fret space', 'Just in front of the fret'],
            'explanation': 'Press just behind the fret (toward the nut) for clean tone with minimal effort.',
        },
        {
            'question': 'What is "alternating fingers" technique?',
            'correct': 'Switching between index and middle fingers',
            'wrong': ['Using only the thumb', 'Using a pick alternately', 'Switching between hands'],
            'explanation': 'Alternating between index and middle fingers allows faster, even playing.',
        },
        {
            'question': 'Playing closer to the bridge produces what kind of tone?',
            'correct': 'Brighter, more treble',
            'wrong': ['Warmer, more bass', 'No difference', 'Quieter sound'],
            'explanation': 'Near bridge = brighter tone. Near neck = warmer, fuller tone.',
        },
        {
            'question': 'What is a hammer-on?',
            'correct': 'Fretting a note without plucking',
            'wrong': ['A type of slide', 'Bending a string', 'Palm muting'],
            'explanation': 'A hammer-on sounds a note by "hammering" your finger onto the fretboard.',
        },
        {
            'question': 'What is a pull-off?',
            'correct': 'Plucking with fretting finger to sound lower note',
            'wrong': ['Removing your hand completely', 'Bending down', 'A type of slide'],
            'explanation': 'A pull-off sounds a lower note by plucking the string as you lift your finger.',
        },
        {
            'question': 'Why is muting important on bass?',
            'correct': 'To prevent unwanted string noise',
            'wrong': ['To play quieter', 'To change pitch', 'To play faster'],
            'explanation': 'Bass strings ring sympathetically. Muting prevents muddy, unclear sound.',
        },
    ]
    
    q = random.choice(questions)
    return {
        'type': 'technique',
        'title': 'Bass Technique',
        'question': q['question'],
        'correct_answer': q['correct'],
        'options': json.dumps(shuffle_options(q['correct'], q['wrong'])),
        'explanation': q['explanation'],
        'difficulty': difficulty,
    }


# =============================================================================
# MAIN GENERATOR FUNCTION
# =============================================================================

QUIZ_GENERATORS = {
    'fretboard': generate_fretboard_quiz,
    'chord_tones': generate_chord_tones_quiz,
    'interval': generate_interval_quiz,
    'interval_semitones': generate_interval_semitones_quiz,
    'scale_notes': generate_scale_notes_quiz,
    'key_signature': generate_key_signature_quiz,
    'relative_minor': generate_relative_minor_quiz,
    'circle_of_fifths': generate_circle_of_fifths_quiz,
    'chord_formula': generate_chord_formula_quiz,
    'note_to_fret': generate_note_to_fret_quiz,
    'rhythm': generate_rhythm_quiz,
    'technique': generate_technique_quiz,
}

# Group quiz types into categories for the UI
QUIZ_CATEGORIES = {
    'fretboard': ['fretboard', 'note_to_fret'],
    'theory': ['interval', 'interval_semitones', 'key_signature', 'relative_minor', 'circle_of_fifths'],
    'chords': ['chord_tones', 'chord_formula'],
    'scales': ['scale_notes'],
    'rhythm': ['rhythm'],
    'technique': ['technique'],
}


def generate_quiz(quiz_category, difficulty=1):
    """Generate a random quiz question for the given category."""
    if quiz_category not in QUIZ_CATEGORIES:
        quiz_category = 'fretboard'
    
    # Pick a random quiz type from the category
    quiz_types = QUIZ_CATEGORIES[quiz_category]
    quiz_type = random.choice(quiz_types)
    
    generator = QUIZ_GENERATORS.get(quiz_type)
    if not generator:
        generator = generate_fretboard_quiz
    
    return generator(difficulty)
