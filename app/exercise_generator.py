"""
Dynamic exercise generator for bass guitar practice.
This file is now a wrapper around the modular generators.
"""
from .generators import (
    generate_exercise,
    generate_scale_exercise,
    generate_chromatic_exercise,
    generate_arpeggio_exercise,
    generate_chord_progression_exercise,
    generate_rhythm_exercise,
)
from .generators.technique import (
    generate_technique_exercise,
    generate_finger_exercise,
    TECHNIQUES
)
from .generators.theory import generate_interval_exercise

# Re-exporting for backward compatibility
EXERCISE_CATEGORIES = ['scales', 'arpeggios', 'rhythm', 'technique', 'theory']
