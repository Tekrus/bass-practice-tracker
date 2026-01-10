"""
Application-wide configuration and constants for the Bass Practice application.
"""

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

# Common chord progressions
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
    'I-IV': [(0, 'major'), (5, 'major')],
}

# Key signatures (number of sharps positive, flats negative)
KEY_SIGNATURES = {
    'C': 0, 'G': 1, 'D': 2, 'A': 3, 'E': 4, 'B': 5, 'F#': 6,
    'F': -1, 'Bb': -2, 'Eb': -3, 'Ab': -4, 'Db': -5, 'Gb': -6,
}

# Circle of fifths order
CIRCLE_OF_FIFTHS = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#', 'Ab', 'Eb', 'Bb', 'F']

# =============================================================================
# UI & APP CONFIG
# =============================================================================

# UI Color Scheme (HSL based for consistency)
COLORS = {
    'primary': 'hsl(210, 100%, 50%)',    # Blue
    'secondary': 'hsl(280, 80%, 60%)',  # Purple
    'success': 'hsl(140, 70%, 45%)',    # Green
    'warning': 'hsl(40, 90%, 50%)',     # Orange
    'danger': 'hsl(0, 80%, 60%)',       # Red
    'background': 'hsl(220, 20%, 10%)', # Dark space
    'surface': 'hsl(220, 20%, 15%)',    # Card background
    'text': 'hsl(0, 0%, 95%)',          # Main text
    'text_muted': 'hsl(0, 0%, 70%)',    # Muted text
}

# Pagination and display limits
PAGE_SIZE = 20
RECENT_SESSIONS_COUNT = 7
MAX_TAB_WIDTH = 80

# Tempo ranges by difficulty (difficulty level -> (min, max))
TEMPO_RANGES = {
    1: (60, 80),
    2: (70, 100),
    3: (80, 120),
    4: (90, 140),
    5: (100, 180),
}

# Application values
APP_NAME = "Bass Practice Pro"
MASTERY_THRESHOLD = 90.0
DEFAULT_SESSION_DURATION = 30
