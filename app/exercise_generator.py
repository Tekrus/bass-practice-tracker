"""
Dynamic exercise generator for bass guitar practice.
Generates exercises algorithmically based on music theory.
"""
import random
import json

# =============================================================================
# MUSIC THEORY CONSTANTS
# =============================================================================

NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
NOTES_FLAT = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']

# Bass string open notes (string number -> note index in NOTES)
BASS_STRINGS = {
    1: 7,   # G string - index 7
    2: 2,   # D string - index 2  
    3: 9,   # A string - index 9
    4: 4,   # E string - index 4
}
STRING_NAMES = {1: 'G', 2: 'D', 3: 'A', 4: 'E'}

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
    'chromatic': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
}

# Arpeggio formulas
ARPEGGIO_FORMULAS = {
    'major triad': [0, 4, 7],
    'minor triad': [0, 3, 7],
    'diminished triad': [0, 3, 6],
    'augmented triad': [0, 4, 8],
    'major 7th': [0, 4, 7, 11],
    'minor 7th': [0, 3, 7, 10],
    'dominant 7th': [0, 4, 7, 10],
    'diminished 7th': [0, 3, 6, 9],
    'half-diminished 7th': [0, 3, 6, 10],
    'minor-major 7th': [0, 3, 7, 11],
    'major 9th': [0, 4, 7, 11, 14],
    'minor 9th': [0, 3, 7, 10, 14],
    'dominant 9th': [0, 4, 7, 10, 14],
}

# Common chord progressions (as roman numerals with semitone offsets from key)
CHORD_PROGRESSIONS = {
    'I-IV-V': [(0, 'major'), (5, 'major'), (7, 'major')],
    'I-V-vi-IV': [(0, 'major'), (7, 'major'), (9, 'minor'), (5, 'major')],
    'ii-V-I': [(2, 'minor 7th'), (7, 'dominant 7th'), (0, 'major 7th')],
    'I-vi-IV-V': [(0, 'major'), (9, 'minor'), (5, 'major'), (7, 'major')],
    'i-bVII-bVI-V': [(0, 'minor'), (10, 'major'), (8, 'major'), (7, 'major')],
    'I-bVII-IV': [(0, 'major'), (10, 'major'), (5, 'major')],
    '12-bar blues': [(0, 'dominant 7th'), (0, 'dominant 7th'), (0, 'dominant 7th'), (0, 'dominant 7th'),
                     (5, 'dominant 7th'), (5, 'dominant 7th'), (0, 'dominant 7th'), (0, 'dominant 7th'),
                     (7, 'dominant 7th'), (5, 'dominant 7th'), (0, 'dominant 7th'), (7, 'dominant 7th')],
    'i-iv-v': [(0, 'minor'), (5, 'minor'), (7, 'minor')],
    'I-IV': [(0, 'major'), (5, 'major')],  # Funk vamp
}

# Rhythm patterns (as beat subdivisions - 1=quarter, 0.5=eighth, 0.25=sixteenth)
RHYTHM_PATTERNS = {
    'whole notes': [4],
    'half notes': [2, 2],
    'quarter notes': [1, 1, 1, 1],
    'eighth notes': [0.5] * 8,
    'eighth note groove': [1, 0.5, 0.5, 1, 0.5, 0.5],
    'syncopated': [0.5, 1, 0.5, 0.5, 1, 0.5],
    'dotted quarter': [1.5, 0.5, 1.5, 0.5],
    'shuffle': [0.67, 0.33] * 4,  # Triplet feel
    'sixteenth groove': [0.25, 0.25, 0.5, 0.25, 0.25, 0.5, 0.25, 0.25, 0.5, 0.5],
    'funk pattern': [0.5, 0.25, 0.25, 0.5, 0.5, 0.25, 0.25, 0.5, 0.5],
}

# Technique exercises
TECHNIQUES = {
    'hammer_on': 'Hammer-on',
    'pull_off': 'Pull-off',
    'slide': 'Slide',
    'vibrato': 'Vibrato',
    'muting': 'Muting',
    'ghost_notes': 'Ghost Notes',
    'string_crossing': 'String Crossing',
    'position_shift': 'Position Shift',
    'alternating_fingers': 'Alternating Fingers',
    'rake': 'Rake',
}

# Tempo ranges by difficulty
TEMPO_RANGES = {
    1: (50, 70),
    2: (60, 80),
    3: (70, 100),
    4: (80, 120),
    5: (90, 140),
}

# Keys by difficulty (natural keys first, then sharps/flats)
KEYS_BY_DIFFICULTY = {
    1: ['C', 'G', 'A', 'E', 'D'],
    2: ['C', 'G', 'A', 'E', 'D', 'F', 'B'],
    3: NOTES[:7],  # Natural notes
    4: NOTES[:10],
    5: NOTES,
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


def get_scale_notes(root, scale_type):
    """Get the notes in a scale."""
    root_idx = get_note_index(root)
    formula = SCALE_FORMULAS.get(scale_type, SCALE_FORMULAS['major'])
    use_flats = 'b' in root or root in ['F', 'Bb', 'Eb', 'Ab', 'Db', 'Gb']
    return [get_note_at_index(root_idx + interval, use_flats) for interval in formula]


def get_arpeggio_notes(root, arpeggio_type):
    """Get the notes in an arpeggio."""
    root_idx = get_note_index(root)
    formula = ARPEGGIO_FORMULAS.get(arpeggio_type, ARPEGGIO_FORMULAS['major triad'])
    use_flats = 'b' in root or root in ['F', 'Bb', 'Eb', 'Ab', 'Db', 'Gb']
    return [get_note_at_index(root_idx + interval, use_flats) for interval in formula]


def get_fret_for_note(string_num, note):
    """Get the fret number for a note on a specific string (within first 12 frets)."""
    open_note_idx = BASS_STRINGS[string_num]
    target_idx = get_note_index(note)
    fret = (target_idx - open_note_idx) % 12
    return fret


def generate_tab(notes_per_string, include_timing=False):
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


def pick_key(difficulty):
    """Pick a random key appropriate for the difficulty level."""
    keys = KEYS_BY_DIFFICULTY.get(difficulty, NOTES)
    return random.choice(keys)


def pick_tempo(difficulty):
    """Pick a random tempo appropriate for the difficulty level."""
    min_tempo, max_tempo = TEMPO_RANGES.get(difficulty, (60, 100))
    # Round to nearest 5
    return round(random.randint(min_tempo, max_tempo) / 5) * 5


# =============================================================================
# EXERCISE GENERATORS
# =============================================================================

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


def generate_technique_exercise(difficulty):
    """Generate a technique-focused exercise."""
    key = pick_key(difficulty)
    tempo = pick_tempo(max(1, difficulty - 1))  # Slower tempo for technique work
    
    # Techniques by difficulty
    if difficulty <= 2:
        tech_list = ['alternating_fingers', 'muting', 'string_crossing']
    elif difficulty <= 3:
        tech_list = ['alternating_fingers', 'muting', 'string_crossing', 'hammer_on', 'pull_off', 'position_shift']
    else:
        tech_list = list(TECHNIQUES.keys())
    
    technique = random.choice(tech_list)
    technique_name = TECHNIQUES[technique]
    
    # Generate exercise based on technique
    if technique in ['hammer_on', 'pull_off']:
        frets = [5, 7] if technique == 'hammer_on' else [7, 5]
        description = f"Practice {technique_name}s from fret {frets[0]} to fret {frets[1]}."
        instructions = [
            f"Place your finger on fret {frets[0]} of the A string.",
            f"{'Hammer onto' if technique == 'hammer_on' else 'Pull off to'} fret {frets[1]}.",
            "The second note should ring clearly without plucking.",
            f"Start slow at {tempo} BPM.",
        ]
    elif technique == 'slide':
        description = "Practice smooth slides between notes."
        instructions = [
            "Start on fret 5 of the A string.",
            "Slide up to fret 7 while maintaining pressure.",
            "Slide back down to fret 5.",
            f"Keep steady timing at {tempo} BPM.",
        ]
    elif technique == 'string_crossing':
        description = "Practice clean transitions between strings."
        instructions = [
            "Play fret 5 on the E string.",
            "Cross to fret 5 on the A string.",
            "Continue to D and G strings.",
            "Mute each string as you leave it.",
            f"Use {tempo} BPM with quarter notes.",
        ]
    elif technique == 'ghost_notes':
        description = "Practice adding ghost notes between main notes."
        instructions = [
            "Play a simple groove on the root note.",
            "Add muted 'ghost' notes with your fretting hand.",
            "Ghost notes add percussive feel without pitch.",
            f"Start at {tempo} BPM.",
        ]
    elif technique == 'position_shift':
        scale_notes = get_scale_notes(key, 'major')
        description = f"Practice shifting positions smoothly in {key} major."
        instructions = [
            f"Play the {key} major scale starting at fret 3.",
            "Shift to position 7 after the 5th note.",
            "Keep the slide smooth and in time.",
            f"Use {tempo} BPM.",
        ]
    else:
        description = f"Practice {technique_name} technique for clean, controlled playing."
        instructions = [
            f"Focus on {technique_name} technique.",
            "Start slowly and prioritize control over speed.",
            f"Use {tempo} BPM with eighth notes.",
            "Gradually increase tempo as you improve.",
        ]
    
    tips = [
        f"{technique_name} is essential for expressive bass playing.",
        "Slow practice builds muscle memory faster than fast practice.",
        "Record yourself to identify areas for improvement.",
    ]
    
    return {
        'title': f'{technique_name} Exercise',
        'category': 'technique',
        'subcategory': technique,
        'difficulty': difficulty,
        'duration': 3 + difficulty,
        'key': key,
        'tempo': tempo,
        'technique': technique,
        'technique_name': technique_name,
        'instructions': '\n'.join(instructions),
        'tips': random.choice(tips),
        'description': description,
    }


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


def generate_finger_exercise(difficulty):
    """Generate a finger independence/strength exercise."""
    tempo = pick_tempo(max(1, difficulty - 1))
    
    # Finger patterns
    patterns = {
        1: ['1-2-3-4', '4-3-2-1'],
        2: ['1-2-3-4', '4-3-2-1', '1-3-2-4', '4-2-3-1'],
        3: ['1-2-3-4', '4-3-2-1', '1-3-2-4', '4-2-3-1', '1-4-2-3', '3-2-4-1'],
        4: ['1-2-3-4', '4-3-2-1', '1-3-2-4', '4-2-3-1', '1-4-2-3', '3-2-4-1', 
            '1-4-3-2', '2-3-4-1', '1-2-4-3', '3-4-2-1'],
        5: ['1-2-3-4', '4-3-2-1', '1-3-2-4', '4-2-3-1', '1-4-2-3', '3-2-4-1',
            '1-4-3-2', '2-3-4-1', '1-2-4-3', '3-4-2-1', '2-1-4-3', '3-4-1-2'],
    }
    
    pattern_list = patterns.get(difficulty, patterns[1])
    pattern = random.choice(pattern_list)
    
    # String movement
    string_patterns = ['single string']
    if difficulty >= 2:
        string_patterns.append('across strings ascending')
    if difficulty >= 3:
        string_patterns.extend(['across strings descending', 'spider walk'])
    
    string_pattern = random.choice(string_patterns)
    
    instructions = [
        f"Play the finger pattern: {pattern}",
        f"Use one finger per fret, starting at fret 5.",
        f"Movement: {string_pattern}",
        f"Start at {tempo} BPM with eighth notes.",
    ]
    
    if difficulty >= 2:
        instructions.append("Keep all fingers close to the fretboard.")
    if difficulty >= 3:
        instructions.append("Maintain even pressure and volume on each note.")
    if difficulty >= 4:
        instructions.append("Increase tempo by 5 BPM after 1 minute of clean playing.")
    
    tips = [
        "The 'spider' exercise builds finger independence.",
        "Keep your thumb behind the neck for proper form.",
        "Relax your hand - tension slows you down.",
        "Focus on the weakest finger (usually the pinky).",
    ]
    
    return {
        'title': f'Finger Pattern: {pattern}',
        'category': 'technique',
        'subcategory': 'finger_independence',
        'difficulty': difficulty,
        'duration': 3 + difficulty,
        'tempo': tempo,
        'pattern': pattern,
        'string_pattern': string_pattern,
        'instructions': '\n'.join(instructions),
        'tips': random.choice(tips),
        'description': f"Build finger independence and strength with the {pattern} pattern.",
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


# =============================================================================
# MAIN GENERATOR FUNCTION
# =============================================================================

EXERCISE_GENERATORS = {
    'scales': [generate_scale_exercise, generate_chromatic_exercise],
    'arpeggios': [generate_arpeggio_exercise],
    'rhythm': [generate_chord_progression_exercise, generate_rhythm_exercise],
    'technique': [generate_technique_exercise, generate_finger_exercise],
    'theory': [generate_interval_exercise],
}

EXERCISE_CATEGORIES = list(EXERCISE_GENERATORS.keys())


def generate_exercise(category=None, difficulty=1):
    """Generate a random exercise for the given category."""
    if category is None or category not in EXERCISE_GENERATORS:
        category = random.choice(EXERCISE_CATEGORIES)
    
    generators = EXERCISE_GENERATORS[category]
    generator = random.choice(generators)
    
    return generator(difficulty)


def generate_practice_session(duration_minutes, skill_level):
    """Generate a complete practice session with multiple exercises."""
    exercises = []
    remaining_time = duration_minutes
    
    # Structure: warm-up, main work, cool-down
    phases = [
        ('warm-up', 0.15, ['technique', 'scales']),  # 15% warm-up
        ('technique', 0.35, ['technique', 'scales', 'arpeggios']),  # 35% technique
        ('musical', 0.40, ['rhythm', 'arpeggios', 'theory']),  # 40% musical
        ('cool-down', 0.10, ['scales', 'arpeggios']),  # 10% cool-down
    ]
    
    for phase_name, phase_ratio, categories in phases:
        phase_time = int(duration_minutes * phase_ratio)
        if phase_time < 3:
            phase_time = 3
        
        while phase_time > 0 and remaining_time > 0:
            category = random.choice(categories)
            
            # Adjust difficulty based on phase
            if phase_name == 'warm-up':
                diff = max(1, skill_level - 1)
            elif phase_name == 'cool-down':
                diff = max(1, skill_level - 1)
            else:
                diff = skill_level
            
            exercise = generate_exercise(category, diff)
            exercise['phase'] = phase_name
            
            exercise_time = exercise.get('duration', 5)
            if exercise_time <= phase_time and exercise_time <= remaining_time:
                exercises.append(exercise)
                phase_time -= exercise_time
                remaining_time -= exercise_time
            else:
                break
    
    return exercises
