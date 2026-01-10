import random
from .utils import pick_key, pick_tempo
from .scales import get_scale_notes

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
