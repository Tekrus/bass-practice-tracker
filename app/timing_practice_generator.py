"""
Timing practice game generator for bass practice.

Generates various timing exercise patterns for practicing tight rhythm.
"""
import random

# Game modes
GAME_MODES = {
    'groove': {
        'name': 'Groove Lock',
        'description': 'Play steady quarter notes to lock into the groove. Focus on feel.',
        'icon': 'music-note-beamed',
        'color': '#22c55e',  # green
    },
    'precision': {
        'name': 'Precision Strike',
        'description': 'Hit notes at exact beats. Timing windows get tighter as you level up.',
        'icon': 'bullseye',
        'color': '#3b82f6',  # blue
    },
    'subdivisions': {
        'name': 'Subdivision Master',
        'description': 'Practice eighth notes, triplets, and sixteenths. Build your subdivision skills.',
        'icon': 'grid-3x3',
        'color': '#f59e0b',  # amber
    },
    'endurance': {
        'name': 'Endurance Run',
        'description': 'Keep the groove going as long as possible. Tempo gradually increases.',
        'icon': 'speedometer2',
        'color': '#ef4444',  # red
    },
    'syncopation': {
        'name': 'Syncopation Challenge',
        'description': 'Hit off-beat accents and syncopated patterns. Test your rhythmic independence.',
        'icon': 'shuffle',
        'color': '#8b5cf6',  # purple
    },
}

# Difficulty levels
DIFFICULTY_LEVELS = {
    1: {
        'name': 'Beginner',
        'perfect_window_ms': 80,  # +/- 80ms for perfect
        'good_window_ms': 150,    # +/- 150ms for good
        'tempo_range': (60, 90),
        'pattern_complexity': 1,
    },
    2: {
        'name': 'Easy',
        'perfect_window_ms': 60,
        'good_window_ms': 120,
        'tempo_range': (70, 100),
        'pattern_complexity': 2,
    },
    3: {
        'name': 'Medium',
        'perfect_window_ms': 45,
        'good_window_ms': 90,
        'tempo_range': (80, 120),
        'pattern_complexity': 3,
    },
    4: {
        'name': 'Hard',
        'perfect_window_ms': 30,
        'good_window_ms': 60,
        'tempo_range': (90, 140),
        'pattern_complexity': 4,
    },
    5: {
        'name': 'Expert',
        'perfect_window_ms': 20,
        'good_window_ms': 40,
        'tempo_range': (100, 160),
        'pattern_complexity': 5,
    },
}

# Rhythm patterns (in beats, 1 = quarter note)
RHYTHM_PATTERNS = {
    'groove': {
        1: [[1, 1, 1, 1]],  # Simple quarter notes
        2: [[1, 1, 1, 1], [1, 0.5, 0.5, 1, 1]],  # Add some eighths
        3: [[1, 1, 1, 1], [1, 0.5, 0.5, 1, 1], [0.5, 0.5, 1, 0.5, 0.5, 1]],
        4: [[1, 0.5, 0.5, 0.5, 0.5, 1, 1], [0.5, 0.5, 0.5, 0.5, 1, 1, 1]],
        5: [[0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]],  # All eighths
    },
    'subdivisions': {
        1: [[1, 1, 1, 1]],  # Quarter notes
        2: [[0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]],  # Eighth notes
        3: [[0.333, 0.333, 0.333] * 4],  # Triplets (approximation)
        4: [[0.25, 0.25, 0.25, 0.25] * 4],  # Sixteenth notes
        5: [[0.25, 0.25, 0.5, 0.25, 0.25, 0.5, 0.5, 0.5]],  # Mixed
    },
    'syncopation': {
        1: [[1, 1, 1, 1]],  # On beats
        2: [[0.5, 1, 0.5, 1, 1]],  # Simple offbeat
        3: [[0.5, 0.5, 0.5, 1.5, 0.5, 0.5]],  # Syncopated
        4: [[0.5, 1.5, 0.5, 1.5]],  # Strong syncopation
        5: [[0.75, 0.75, 0.5, 0.75, 0.75, 0.5]],  # Complex syncopation
    },
}

# Scoring
SCORE_PERFECT = 100
SCORE_GOOD = 50
SCORE_EARLY = 10
SCORE_LATE = 10
SCORE_MISS = 0

# Streak bonuses
STREAK_MULTIPLIERS = {
    5: 1.5,
    10: 2.0,
    20: 2.5,
    50: 3.0,
    100: 4.0,
}


def generate_timing_exercise(game_mode, difficulty=1, tempo=None, duration_bars=4):
    """
    Generate a timing exercise based on game mode and difficulty.
    
    Args:
        game_mode: One of the GAME_MODES keys
        difficulty: 1-5 difficulty level
        tempo: BPM (if None, random from difficulty range)
        duration_bars: Number of bars in the exercise
    
    Returns:
        dict with exercise configuration
    """
    if game_mode not in GAME_MODES:
        game_mode = 'groove'
    
    difficulty = max(1, min(5, difficulty))
    diff_config = DIFFICULTY_LEVELS[difficulty]
    
    # Determine tempo
    if tempo is None:
        tempo = random.randint(*diff_config['tempo_range'])
    
    # Get mode info
    mode_info = GAME_MODES[game_mode]
    
    # Generate beat pattern based on mode
    if game_mode == 'precision':
        # Simple consistent beats for precision mode
        pattern = [1] * (4 * duration_bars)  # Quarter notes
    elif game_mode == 'endurance':
        # Starts simple, can get complex
        pattern = [1] * (4 * duration_bars)
    elif game_mode in RHYTHM_PATTERNS:
        # Get patterns for this mode and complexity
        complexity = min(diff_config['pattern_complexity'], 5)
        available_patterns = RHYTHM_PATTERNS[game_mode].get(complexity, [[1, 1, 1, 1]])
        
        # Build the full pattern
        pattern = []
        for _ in range(duration_bars):
            bar_pattern = random.choice(available_patterns)
            pattern.extend(bar_pattern)
    else:
        pattern = [1] * (4 * duration_bars)
    
    # Calculate beat times in milliseconds
    beat_duration_ms = 60000 / tempo  # ms per quarter note
    
    beat_times = []
    current_time = 0
    for note_value in pattern:
        beat_times.append(current_time)
        current_time += beat_duration_ms * note_value
    
    return {
        'game_mode': game_mode,
        'mode_name': mode_info['name'],
        'mode_description': mode_info['description'],
        'mode_icon': mode_info['icon'],
        'mode_color': mode_info['color'],
        'difficulty': difficulty,
        'difficulty_name': diff_config['name'],
        'tempo': tempo,
        'perfect_window_ms': diff_config['perfect_window_ms'],
        'good_window_ms': diff_config['good_window_ms'],
        'pattern': pattern,
        'beat_times': beat_times,
        'total_notes': len(beat_times),
        'duration_ms': current_time,
        'duration_bars': duration_bars,
    }


def calculate_hit_quality(timing_offset_ms, perfect_window, good_window):
    """
    Determine the quality of a hit based on timing offset.
    
    Args:
        timing_offset_ms: Difference from perfect timing (can be negative for early)
        perfect_window: +/- ms for perfect hit
        good_window: +/- ms for good hit
    
    Returns:
        tuple: (quality, score, is_early)
    """
    abs_offset = abs(timing_offset_ms)
    is_early = timing_offset_ms < 0
    
    if abs_offset <= perfect_window:
        return ('perfect', SCORE_PERFECT, is_early)
    elif abs_offset <= good_window:
        return ('good', SCORE_GOOD, is_early)
    elif is_early:
        return ('early', SCORE_EARLY, True)
    else:
        return ('late', SCORE_LATE, False)


def calculate_session_score(hits, streak_bonus=True):
    """
    Calculate total score for a timing session.
    
    Args:
        hits: List of hit dictionaries with 'quality' and 'score' keys
        streak_bonus: Whether to apply streak multipliers
    
    Returns:
        dict with score breakdown
    """
    total_score = 0
    current_streak = 0
    best_streak = 0
    perfect_count = 0
    good_count = 0
    early_count = 0
    late_count = 0
    miss_count = 0
    timing_offsets = []
    
    for hit in hits:
        quality = hit.get('quality', 'miss')
        base_score = hit.get('score', 0)
        offset = hit.get('offset_ms', 0)
        
        if quality == 'perfect':
            perfect_count += 1
            current_streak += 1
            timing_offsets.append(offset)
        elif quality == 'good':
            good_count += 1
            current_streak += 1
            timing_offsets.append(offset)
        elif quality == 'early':
            early_count += 1
            current_streak = 0
        elif quality == 'late':
            late_count += 1
            current_streak = 0
        else:
            miss_count += 1
            current_streak = 0
        
        # Apply streak multiplier
        if streak_bonus and current_streak > 0:
            multiplier = 1.0
            for threshold, mult in sorted(STREAK_MULTIPLIERS.items()):
                if current_streak >= threshold:
                    multiplier = mult
            base_score = int(base_score * multiplier)
        
        total_score += base_score
        best_streak = max(best_streak, current_streak)
    
    total_notes = perfect_count + good_count + early_count + late_count + miss_count
    avg_timing = sum(timing_offsets) / len(timing_offsets) if timing_offsets else 0
    
    return {
        'total_score': total_score,
        'total_notes': total_notes,
        'perfect_hits': perfect_count,
        'good_hits': good_count,
        'early_hits': early_count,
        'late_hits': late_count,
        'missed_notes': miss_count,
        'best_streak': best_streak,
        'final_streak': current_streak,
        'average_timing_ms': round(avg_timing, 2),
        'accuracy_percentage': round((perfect_count + good_count) / total_notes * 100, 1) if total_notes > 0 else 0,
        'perfect_percentage': round(perfect_count / total_notes * 100, 1) if total_notes > 0 else 0,
    }


def get_difficulty_for_accuracy(recent_accuracy, current_difficulty):
    """
    Adjust difficulty based on recent performance.
    
    Args:
        recent_accuracy: Accuracy percentage from recent sessions
        current_difficulty: Current difficulty level
    
    Returns:
        Recommended difficulty level
    """
    if recent_accuracy >= 90:
        return min(5, current_difficulty + 1)
    elif recent_accuracy >= 75:
        return current_difficulty
    elif recent_accuracy >= 50:
        return max(1, current_difficulty - 1)
    else:
        return max(1, current_difficulty - 2)


def generate_practice_tips(stats):
    """
    Generate personalized tips based on session statistics.
    
    Args:
        stats: Dictionary with session statistics
    
    Returns:
        List of tip strings
    """
    tips = []
    
    if stats['early_hits'] > stats['late_hits'] * 2:
        tips.append("You're rushing! Try to relax and let the beat come to you.")
    elif stats['late_hits'] > stats['early_hits'] * 2:
        tips.append("You're dragging behind the beat. Focus on anticipating the click.")
    
    if stats['perfect_percentage'] >= 80:
        tips.append("Excellent precision! Consider increasing the difficulty or tempo.")
    elif stats['perfect_percentage'] < 30:
        tips.append("Focus on the first beat of each measure to anchor your timing.")
    
    if stats['best_streak'] >= 20:
        tips.append(f"Great streak of {stats['best_streak']}! Consistency is key.")
    
    if abs(stats['average_timing_ms']) > 30:
        direction = "early" if stats['average_timing_ms'] < 0 else "late"
        tips.append(f"Your average timing is {abs(stats['average_timing_ms']):.0f}ms {direction}. Work on centering your feel.")
    
    if not tips:
        tips.append("Keep practicing! Consistent timing takes time to develop.")
    
    return tips
