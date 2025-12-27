"""
Dynamic ear training exercise generator for bass guitar practice.
Generates exercises algorithmically based on music theory.
"""
import random
import json

# =============================================================================
# MUSIC THEORY CONSTANTS
# =============================================================================

NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
NOTES_FLAT = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']

# Intervals (name -> semitones)
INTERVALS = {
    'm2': 1, 'M2': 2, 'm3': 3, 'M3': 4, 'P4': 5,
    'tritone': 6, 'P5': 7, 'm6': 8, 'M6': 9, 'm7': 10, 'M7': 11, 'P8': 12
}

# Reverse mapping (semitones -> name)
INTERVALS_REVERSE = {
    1: 'm2', 2: 'M2', 3: 'm3', 4: 'M3', 5: 'P4',
    6: 'tritone', 7: 'P5', 8: 'm6', 9: 'M6', 10: 'm7', 11: 'M7', 12: 'P8'
}

# Chord formulas (intervals from root in semitones)
CHORD_FORMULAS = {
    'major': [0, 4, 7],
    'minor': [0, 3, 7],
    'diminished': [0, 3, 6],
    'augmented': [0, 4, 8],
    'sus2': [0, 2, 7],
    'sus4': [0, 5, 7],
    'major7': [0, 4, 7, 11],
    'minor7': [0, 3, 7, 10],
    'dominant7': [0, 4, 7, 10],
    'diminished7': [0, 3, 6, 9],
    'half-diminished7': [0, 3, 6, 10],
    'minor-major7': [0, 3, 7, 11],
}

# Scale degree to semitones mapping
SCALE_DEGREES = {
    '1': 0, '2': 2, '3': 4, '4': 5, '5': 7, '6': 9, '7': 11, '8': 12,
    'b2': 1, 'b3': 3, 'b5': 6, 'b6': 8, 'b7': 10,
    '#4': 6, '#5': 8
}

# Reverse mapping (semitones -> scale degree)
SCALE_DEGREES_REVERSE = {
    0: '1', 1: 'b2', 2: '2', 3: 'b3', 4: '3', 5: '4', 6: 'b5', 7: '5',
    8: 'b6', 9: '6', 10: 'b7', 11: '7', 12: '8'
}


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


def get_random_wrong_intervals(correct_interval, count=3):
    """Generate plausible wrong interval options."""
    correct_semitones = INTERVALS.get(correct_interval, 1)
    wrong_options = []
    
    # Prioritize nearby intervals (common mistakes)
    offsets = [-2, -1, 1, 2, -3, 3, 5, 7]
    random.shuffle(offsets)
    
    for offset in offsets:
        wrong_semitones = correct_semitones + offset
        if 1 <= wrong_semitones <= 12:
            wrong_interval = INTERVALS_REVERSE.get(wrong_semitones)
            if wrong_interval and wrong_interval != correct_interval and wrong_interval not in wrong_options:
                wrong_options.append(wrong_interval)
                if len(wrong_options) >= count:
                    break
    
    return wrong_options


def get_random_wrong_chords(correct_chord, count=3):
    """Generate plausible wrong chord options."""
    wrong_options = []
    all_chords = list(CHORD_FORMULAS.keys())
    
    # Remove correct answer
    other_chords = [c for c in all_chords if c != correct_chord]
    random.shuffle(other_chords)
    
    # Select wrong options
    wrong_options = other_chords[:count]
    
    return wrong_options


def shuffle_options(correct, wrong_options):
    """Shuffle correct answer with wrong options."""
    options = [correct] + wrong_options
    random.shuffle(options)
    return options


# =============================================================================
# EXERCISE GENERATORS
# =============================================================================

def generate_interval_exercise(difficulty):
    """Generate an interval identification exercise."""
    # Intervals by difficulty
    if difficulty <= 1:
        available_intervals = ['m2', 'M2', 'P4', 'P5', 'P8']
    elif difficulty <= 2:
        available_intervals = ['m2', 'M2', 'm3', 'M3', 'P4', 'P5', 'm6', 'M6', 'P8']
    elif difficulty <= 3:
        available_intervals = ['m2', 'M2', 'm3', 'M3', 'P4', 'tritone', 'P5', 'm6', 'M6', 'm7', 'M7', 'P8']
    else:
        available_intervals = list(INTERVALS.keys())
    
    # Pick a random interval
    correct_interval = random.choice(available_intervals)
    
    # Pick a random root note
    if difficulty <= 2:
        root_note = random.choice(NOTES[:7])  # Natural notes
    else:
        root_note = random.choice(NOTES)
    
    # Generate wrong options
    wrong_options = get_random_wrong_intervals(correct_interval, 3)
    
    # Ensure we have enough options
    while len(wrong_options) < 3:
        all_intervals = list(INTERVALS.keys())
        wrong = random.choice(all_intervals)
        if wrong != correct_interval and wrong not in wrong_options:
            wrong_options.append(wrong)
    
    options = shuffle_options(correct_interval, wrong_options[:3])
    
    # Generate hints based on interval
    hints_map = {
        'm2': "Think 'Jaws' theme",
        'M2': "Think beginning of a major scale",
        'm3': "Think 'Greensleeves'",
        'M3': "Think 'Oh When the Saints'",
        'P4': "Think 'Here Comes the Bride'",
        'tritone': "Think 'The Simpsons' theme",
        'P5': "Think 'Star Wars' theme",
        'm6': "Think 'The Entertainer'",
        'M6': "Think 'NBC theme'",
        'm7': "Think 'Somewhere' from West Side Story",
        'M7': "Think 'Take On Me'",
        'P8': "Think 'Somewhere Over the Rainbow'"
    }
    
    return {
        'type': 'interval',
        'title': f'{correct_interval.upper()} Interval',
        'description': f'Identify the interval from {root_note}.',
        'root_note': root_note,
        'correct_answer': correct_interval,
        'options': json.dumps(options),
        'hints': hints_map.get(correct_interval, 'Listen carefully to the interval quality'),
        'difficulty': difficulty
    }


def generate_chord_exercise(difficulty):
    """Generate a chord quality identification exercise."""
    # Chord types by difficulty
    if difficulty <= 1:
        available_chords = ['major', 'minor']
    elif difficulty <= 2:
        available_chords = ['major', 'minor', 'diminished', 'augmented']
    elif difficulty <= 3:
        available_chords = ['major', 'minor', 'diminished', 'augmented', 'sus2', 'sus4', 'major7', 'minor7', 'dominant7']
    else:
        available_chords = list(CHORD_FORMULAS.keys())
    
    # Pick a random chord type
    correct_chord = random.choice(available_chords)
    
    # Pick a random root note
    if difficulty <= 2:
        root_note = random.choice(NOTES[:7])  # Natural notes
    else:
        root_note = random.choice(NOTES)
    
    # Generate wrong options
    wrong_options = get_random_wrong_chords(correct_chord, 3)
    
    options = shuffle_options(correct_chord, wrong_options)
    
    # Generate hints
    hints_map = {
        'major': 'Sounds happy and stable',
        'minor': 'Sounds sad or mysterious',
        'diminished': 'Sounds unstable and tense',
        'augmented': 'Sounds like it\'s floating upward',
        'major7': 'Smooth and sophisticated',
        'minor7': 'Mellow and jazzy',
        'dominant7': 'Has tension needing resolution',
        'sus2': 'Open and suspended',
        'sus4': 'Open and suspended',
    }
    
    return {
        'type': 'chord',
        'title': f'{root_note} Chord Quality',
        'description': f'Identify the quality of the {root_note} chord.',
        'root_note': root_note,
        'correct_answer': correct_chord,
        'options': json.dumps(options),
        'hints': hints_map.get(correct_chord, 'Listen to the chord quality'),
        'difficulty': difficulty
    }


def generate_melody_exercise(difficulty):
    """Generate a melody transcription exercise."""
    # Pick a random root note
    if difficulty <= 2:
        root_note = random.choice(NOTES[:7])  # Natural notes
    else:
        root_note = random.choice(NOTES)
    
    # Melody patterns by difficulty
    if difficulty <= 1:
        # Simple 3-4 note patterns
        patterns = [
            ['1', '3', '5'],
            ['1', '3', '5', '3'],
            ['1', '5', '3', '1'],
        ]
    elif difficulty <= 2:
        # Simple arpeggio-based patterns
        patterns = [
            ['1', '3', '5', '3'],
            ['1', 'b3', '5', 'b3'],
            ['1', '5', '3', '1'],
            ['1', '3', '1', '5'],
        ]
    elif difficulty <= 3:
        # Pentatonic and scale-based patterns
        patterns = [
            ['1', 'b3', '4', '5', 'b7'],
            ['1', '2', '3', '5', '6'],
            ['1', '3', '5', 'b7', '5'],
            ['1', 'b3', '5', 'b7', '1'],
        ]
    else:
        # More complex patterns
        patterns = [
            ['1', 'b3', '4', '5', 'b7', '5'],
            ['1', '1', '5', '5', 'b7', 'b7', '5'],
            ['1', '3', '5', '3', '1', '5', '1'],
            ['1', '5', '1', '5', '4', '5', '1'],
            ['1', 'b3', '5', 'b7', '1', 'b3', '5'],
        ]
    
    # Pick a random pattern
    pattern = random.choice(patterns)
    correct_answer = '-'.join(pattern)
    
    # Generate wrong options by modifying the pattern
    wrong_options = []
    
    # Wrong option 1: Change one note
    wrong1 = pattern.copy()
    idx = random.randint(1, len(wrong1) - 1)
    wrong1[idx] = random.choice(['2', '3', '4', '5'])
    wrong_options.append('-'.join(wrong1))
    
    # Wrong option 2: Different pattern length
    if len(pattern) > 3:
        wrong2 = pattern[:-1]
        wrong_options.append('-'.join(wrong2))
    else:
        wrong2 = pattern + ['3']
        wrong_options.append('-'.join(wrong2))
    
    # Wrong option 3: Scrambled pattern
    wrong3 = pattern.copy()
    random.shuffle(wrong3)
    wrong_options.append('-'.join(wrong3))
    
    # Ensure uniqueness
    wrong_options = list(set([w for w in wrong_options if w != correct_answer]))[:3]
    
    # Fill if needed
    while len(wrong_options) < 3:
        all_patterns = [
            ['1', '2', '3', '2'],
            ['1', '3', '2', '1'],
            ['1', '5', '3', '1'],
            ['1', '1', '3', '3', '5', '5', '3'],
        ]
        wrong = '-'.join(random.choice(all_patterns))
        if wrong != correct_answer and wrong not in wrong_options:
            wrong_options.append(wrong)
    
    options = shuffle_options(correct_answer, wrong_options[:3])
    
    return {
        'type': 'melody',
        'title': 'Melody Transcription',
        'description': f'Transcribe the melody pattern starting from {root_note}.',
        'root_note': root_note,
        'correct_answer': correct_answer,
        'options': json.dumps(options),
        'hints': 'Listen to the scale degrees and pattern',
        'difficulty': difficulty
    }


# =============================================================================
# MAIN GENERATOR FUNCTION
# =============================================================================

def generate_ear_training_exercise(exercise_type, difficulty=1):
    """Generate a random ear training exercise for the given type."""
    if exercise_type == 'interval':
        return generate_interval_exercise(difficulty)
    elif exercise_type == 'chord':
        return generate_chord_exercise(difficulty)
    elif exercise_type == 'melody':
        return generate_melody_exercise(difficulty)
    else:
        # Default to interval
        return generate_interval_exercise(difficulty)

