# Bass Practice Website Implementation Plan

## Project Overview
A local Python web application for bass guitar practice with daily practice generation, progress tracking, and an interactive exercise library. Designed to run locally on Windows for a single user.

## Technology Stack

### Core Technologies
- **Backend Framework**: Flask (simple, lightweight, perfect for local single-user app)
- **Database**: SQLite with SQLAlchemy (no setup required, file-based)
- **Frontend**: HTML/CSS/JavaScript with Bootstrap (easy to use, responsive)
- **Audio**: Web Audio API (browser-based, no Python audio libraries needed)

### Specialized Libraries
- **Charts**: Chart.js (simple, browser-based)
- **Forms**: WTForms (Flask integration)
- **File Storage**: Local file system with pathlib
- **Code Quality**: black, ruff (optional for development)

### Development Tools
- **Environment Management**: python-dotenv
- **Database**: SQLite file (no migrations needed initially)

## Core Features

### 1. User Profile (Local Only)
- **Skill Level**: Self-assessment (beginner/intermediate/advanced, 1-10 scale)
- **Practice Preferences**: 
  - Preferred genres (rock, funk, jazz, blues)
  - Session duration (15, 30, 45, 60, 90 minutes)
  - Bass tuning (standard E, drop D)
- **Goals**: Practice focus areas (technique, theory, performance)

### 2. Exercise Library
- **Categories**:
  - **Scales**: Major/minor pentatonic, diatonic modes, blues
  - **Arpeggios**: Triads, seventh chords
  - **Rhythm**: Rock, funk, jazz, blues patterns
  - **Technique**: Finger strength, string crossing, slap/pop
  - **Theory**: Circle of fifths, chord progressions
  - **Ear Training**: Interval recognition, chord quality, melody playback
  - **Song Practice**: Real songs with bass tabs and chord progressions

- **Difficulty System**: 1-10 scale
- **Exercise Structure**:
  - Title and description
  - Step-by-step instructions
  - Difficulty rating
  - Estimated duration
  - Related exercises
  - Audio examples (for ear training)

### 3. Daily Practice Generator
- **Simple Algorithm**:
  - Based on user skill level
  - Balances categories (scales, technique, rhythm, theory)
  - Ensures variety (rotates exercises)
  - Adapts to session duration

- **Session Structure**:
  - **Warm-up** (5-10 minutes): Basic scales, finger exercises
  - **Technique Focus** (25-35%): Specific technical exercises
  - **Musical Application** (35-45%): Patterns, grooves
  - **Cool-down** (5 minutes): Slow scales, reflection

### 4. Practice Session Interface
- **Timer**: Per-exercise and session timers
- **Metronome**: 
  - Adjustable BPM (40-240)
  - Time signature selection (4/4, 3/4)
  - Visual beat indicator
- **Progress Tracking**:
  - Mark exercises complete
  - Add notes
  - Rate difficulty felt

### 5. Progress Tracking
- **Dashboard**:
  - Current practice streak
  - Total practice time
  - Skills overview
  - Recent activity
  - Songs practiced this week

- **Statistics**:
  - Daily/weekly practice time
  - Exercise completion by category
  - Difficulty progression
  - Practice consistency
  - Ear training accuracy rates
  - Song mastery progress

## Database Schema (Simplified)

### User_Profile Table
```sql
CREATE TABLE user_profile (
    id INTEGER PRIMARY KEY,
    skill_level INTEGER DEFAULT 1, -- 1-10
    skill_category VARCHAR(20) DEFAULT 'beginner',
    preferred_genre VARCHAR(50),
    session_duration INTEGER DEFAULT 30,
    bass_tuning VARCHAR(20) DEFAULT 'standard',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Exercises Table
```sql
CREATE TABLE exercises (
    id INTEGER PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(30) NOT NULL,
    difficulty_level INTEGER NOT NULL, -- 1-10
    estimated_duration INTEGER NOT NULL,
    instructions TEXT,
    prerequisites TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Practice_Sessions Table
```sql
CREATE TABLE practice_sessions (
    id INTEGER PRIMARY KEY,
    session_date DATE NOT NULL,
    planned_duration INTEGER,
    actual_duration INTEGER,
    completed_exercises INTEGER DEFAULT 0,
    session_notes TEXT,
    session_rating INTEGER, -- 1-5 stars
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Session_Exercises Table
```sql
CREATE TABLE session_exercises (
    id INTEGER PRIMARY KEY,
    session_id INTEGER REFERENCES practice_sessions(id),
    exercise_id INTEGER REFERENCES exercises(id),
    order_index INTEGER,
    completed BOOLEAN DEFAULT FALSE,
    actual_duration INTEGER,
    difficulty_felt INTEGER, -- 1-10
    exercise_notes TEXT
);
```

### Progress Table
```sql
CREATE TABLE progress (
    id INTEGER PRIMARY KEY,
    category VARCHAR(30), -- 'scales', 'arpeggios', etc.
    skill_level REAL, -- 0.0-1.0 progress
    exercises_completed INTEGER DEFAULT 0,
    last_practiced DATE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Songs Table
```sql
CREATE TABLE songs (
    id INTEGER PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    artist VARCHAR(100),
    genre VARCHAR(50),
    difficulty_level INTEGER, -- 1-10
    key_signature VARCHAR(10),
    tempo_bpm INTEGER,
    duration_minutes INTEGER,
    bass_notes TEXT, -- JSON array of bass notes/tabs
    chord_progression TEXT, -- JSON array of chords
    youtube_url VARCHAR(255), -- Tutorial/reference video
    practice_notes TEXT,
    mastery_level INTEGER DEFAULT 0, -- 0-5 scale
    last_practiced DATE,
    practice_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Chord_Progressions Table
```sql
CREATE TABLE chord_progressions (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL, -- e.g., "I-IV-V", "ii-V-I"
    progression TEXT NOT NULL, -- JSON array of chord symbols
    genre VARCHAR(50),
    difficulty_level INTEGER,
    description TEXT,
    bass_line_examples TEXT, -- JSON array of example bass lines
    common_songs TEXT, -- Songs using this progression
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Ear_Training_Exercises Table
```sql
CREATE TABLE ear_training_exercises (
    id INTEGER PRIMARY KEY,
    exercise_type VARCHAR(50), -- 'interval', 'chord', 'melody'
    title VARCHAR(100) NOT NULL,
    description TEXT,
    difficulty_level INTEGER,
    audio_file_path VARCHAR(255),
    correct_answer TEXT, -- JSON array of correct answers
    options TEXT, -- JSON array of multiple choice options
    hints TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Ear_Training_Results Table
```sql
CREATE TABLE ear_training_results (
    id INTEGER PRIMARY KEY,
    exercise_id INTEGER REFERENCES ear_training_exercises(id),
    user_answer TEXT,
    correct BOOLEAN,
    response_time_ms INTEGER,
    practiced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Project Structure
```
bass_practice/
├── app/
│   ├── __init__.py              # Flask app initialization
│   ├── main.py                  # Application entry point
│   ├── models.py                # SQLAlchemy models
│   ├── routes.py                # Flask routes
│   ├── forms.py                 # WTForms
│   ├── practice_generator.py    # Practice generation logic
│   ├── utils.py                 # Helper functions
│   ├── ear_training.py          # Ear training logic
│   ├── song_manager.py          # Song practice management
│   │
│   ├── templates/               # Jinja2 templates
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── practice.html
│   │   ├── exercises.html
│   │   ├── progress.html
│   │   ├── settings.html
│   │   ├── ear_training.html
│   │   ├── songs.html
│   │   └── chord_progressions.html
│   │
│   └── static/                  # Static assets
│       ├── css/
│       │   └── styles.css
│       ├── js/
│       │   ├── main.js
│       │   ├── timer.js
│       │   ├── metronome.js
│       │   ├── charts.js
│       │   ├── ear_training.js
│       │   └── songs.js
│       └── audio/
│           ├── metronome/
│           ├── ear_training/
│           └── song_examples/
│
├── data/
│   ├── exercises.json           # Initial exercise data
│   └── bass_practice.db         # SQLite database
│
├── requirements.txt
├── run.py                       # Start the app
└── README.md
```

## Implementation Phases

### Phase 1: Basic Setup (1-2 days)
**Objective**: Get a working Flask app with database

**Tasks**:
1. Set up Flask project structure
2. Configure SQLite database with SQLAlchemy
3. Create basic models (User, Exercise, Practice)
4. Set up basic routing and templates
5. Create initial exercise data (20 exercises)

**Deliverables**:
- Working Flask app on localhost:5000
- Database with basic tables
- Simple exercise list page

---

### Phase 2: Exercise Library (2-3 days)
**Objective**: Build comprehensive exercise system

**Tasks**:
1. Create 50+ exercises across all categories
2. Build exercise browsing interface
3. Add exercise detail pages
4. Implement filtering by category/difficulty
5. Add exercise search functionality

**Deliverables**:
- Complete exercise library
- Exercise browsing and filtering
- Exercise detail pages

---

### Phase 3: Practice Generator (2-3 days)
**Objective**: Build daily practice generation

**Tasks**:
1. Implement practice generation algorithm
2. Create user profile/settings page
3. Build practice session preview
4. Add session customization options
5. Test with different skill levels

**Deliverables**:
- Working practice generator
- User settings page
- Practice preview system

---

### Phase 4: Practice Session Interface (2-3 days)
**Objective**: Create interactive practice experience

**Tasks**:
1. Build active practice session page
2. Implement timer functionality
3. Add metronome with Web Audio API
4. Create exercise completion tracking
5. Add session notes and feedback

**Deliverables**:
- Full practice session workflow
- Working timer and metronome
- Exercise completion tracking

---

### Phase 5: Progress Tracking (2-3 days)
**Objective**: Add progress visualization

**Tasks**:
1. Create dashboard with overview stats
2. Implement progress calculation
3. Add Chart.js for visualization
4. Build practice history page
5. Add streak tracking

**Deliverables**:
- Progress dashboard
- Charts and statistics
- Practice history

---

### Phase 6: Ear Training System (2-3 days)
**Objective**: Add ear training exercises

**Tasks**:
1. Create ear training exercise database
2. Build interval recognition exercises
3. Add chord quality identification
4. Implement melody playback exercises
5. Track accuracy and improvement

**Deliverables**:
- Ear training exercise library
- Interactive ear training interface
- Progress tracking for ear training

---

### Phase 7: Song Practice System (2-3 days)
**Objective**: Add song tracking and playlist generation

**Tasks**:
1. Create song database with bass tabs
2. Build song management interface
3. Implement daily song playlist generator
4. Add song mastery tracking
5. Create song practice statistics

**Deliverables**:
- Song library and management
- Daily song playlist generator
- Song progress tracking

---

### Phase 8: Chord Progression Library (1-2 days)
**Objective**: Add chord progression reference

**Tasks**:
1. Create chord progression database
2. Build progression browser
3. Add bass line examples
4. Link progressions to songs
5. Create practice exercises

**Deliverables**:
- Chord progression library
- Bass line examples
- Integration with song system

---

### Phase 9: Polish & Refinement (1-2 days)
**Objective**: Final improvements

**Tasks**:
1. Improve UI/UX with better styling
2. Add responsive design
3. Fix bugs and edge cases
4. Optimize performance
5. Add user guide

**Deliverables**:
- Polished, professional app
- Responsive design
- Complete documentation

## Key Algorithms

### Practice Generation Algorithm
```python
def generate_practice_session(skill_level, duration_minutes, preferences):
    """
    Generate a balanced practice session based on user skill and preferences.
    """
    # 1. Determine session structure
    structure = calculate_session_structure(duration_minutes)
    # Returns: {'warmup': 5, 'technique': 15, 'musical': 20, 'cooldown': 5}
    
    # 2. Select exercises for each phase
    exercises = []
    
    # Warm-up exercises (lower difficulty)
    warmup_exercises = select_exercises(
        category='warmup',
        difficulty_range=[1, max(3, skill_level - 1)],
        duration=structure['warmup']
    )
    exercises.extend(warmup_exercises)
    
    # Technique exercises (focus on weak areas)
    technique_exercises = select_exercises(
        category='technique',
        difficulty_range=[skill_level - 1, skill_level + 1],
        duration=structure['technique']
    )
    exercises.extend(technique_exercises)
    
    # Musical application exercises
    musical_exercises = select_exercises(
        category='rhythm',
        difficulty_range=[skill_level - 1, skill_level],
        duration=structure['musical'],
        genre=preferences.get('genre')
    )
    exercises.extend(musical_exercises)
    
    # Cool-down exercises
    cooldown_exercises = select_exercises(
        category='scales',
        difficulty_range=[1, skill_level],
        duration=structure['cooldown']
    )
    exercises.extend(cooldown_exercises)
    
    return exercises


def calculate_session_structure(duration):
    """Calculate time allocation for each session phase"""
    structures = {
        15: {'warmup': 3, 'technique': 7, 'musical': 5, 'cooldown': 0},
        30: {'warmup': 5, 'technique': 12, 'musical': 12, 'cooldown': 1},
        45: {'warmup': 5, 'technique': 18, 'musical': 20, 'cooldown': 2},
        60: {'warmup': 8, 'technique': 22, 'musical': 25, 'cooldown': 5},
        90: {'warmup': 10, 'technique': 35, 'musical': 40, 'cooldown': 5}
    }
    return structures.get(duration, structures[30])


def select_exercises(category, difficulty_range, duration, genre=None):
    """Select exercises matching criteria"""
    # Get available exercises from database
    exercises = get_exercises_by_category(category)
    
    # Filter by difficulty
    filtered = [
        ex for ex in exercises
        if difficulty_range[0] <= ex.difficulty <= difficulty_range[1]
    ]
    
    # Filter by genre if specified
    if genre:
        filtered = [ex for ex in filtered if genre in ex.genres]
    
    # Select exercises to fill duration
    selected = []
    total_time = 0
    
    for exercise in filtered:
        if total_time + exercise.duration <= duration:
            selected.append(exercise)
            total_time += exercise.duration
            if total_time >= duration:
                break
    
    return selected
```

### Daily Song Playlist Generator
```python
def generate_daily_song_playlist():
    """
    Generate a playlist of songs to practice based on user's song library
    and practice patterns.
    """
    # Get all songs from user's library
    all_songs = get_user_songs()
    
    # Categorize songs by mastery level
    new_songs = [s for s in all_songs if s.mastery_level <= 1]
    learning_songs = [s for s in all_songs if 2 <= s.mastery_level <= 3]
    review_songs = [s for s in all_songs if s.mastery_level >= 4]
    
    playlist = []
    
    # Priority 1: Songs that haven't been practiced recently
    recently_practiced = get_recently_practiced_songs(days=7)
    overdue_songs = [s for s in all_songs if s not in recently_practiced]
    
    # Priority 2: New songs (introduce 1-2 new songs)
    if new_songs:
        playlist.extend(random.sample(new_songs, min(2, len(new_songs))))
    
    # Priority 3: Songs currently being learned
    if learning_songs:
        playlist.extend(random.sample(learning_songs, min(3, len(learning_songs))))
    
    # Priority 4: Overdue songs for review
    if overdue_songs and len(playlist) < 5:
        remaining_slots = 5 - len(playlist)
        playlist.extend(random.sample(overdue_songs, min(remaining_slots, len(overdue_songs))))
    
    # Priority 5: Mastered songs for maintenance
    if review_songs and len(playlist) < 5:
        remaining_slots = 5 - len(playlist)
        playlist.extend(random.sample(review_songs, min(remaining_slots, len(review_songs))))
    
    return playlist


def update_song_mastery(song_id, practice_quality):
    """
    Update song mastery level based on practice performance.
    """
    song = get_song(song_id)
    
    # Update practice count
    song.practice_count += 1
    song.last_practiced = datetime.now().date()
    
    # Adjust mastery based on practice quality
    if practice_quality >= 4:  # Excellent practice
        song.mastery_level = min(5, song.mastery_level + 1)
    elif practice_quality <= 2:  # Poor practice
        song.mastery_level = max(0, song.mastery_level - 1)
    
    save_song(song)
```

### Ear Training Exercise Logic
```python
def generate_ear_training_exercise(exercise_type, difficulty):
    """
    Generate an ear training exercise based on type and difficulty.
    """
    if exercise_type == 'interval':
        return generate_interval_exercise(difficulty)
    elif exercise_type == 'chord':
        return generate_chord_exercise(difficulty)
    elif exercise_type == 'melody':
        return generate_melody_exercise(difficulty)


def generate_interval_exercise(difficulty):
    """Generate interval recognition exercise"""
    # Select intervals based on difficulty
    if difficulty <= 3:
        intervals = ['P4', 'P5', 'M3', 'm3']
    elif difficulty <= 6:
        intervals = ['P4', 'P5', 'M3', 'm3', 'M2', 'm2', 'M6', 'm6']
    else:
        intervals = ['P4', 'P5', 'M3', 'm3', 'M2', 'm2', 'M6', 'm6', 'M7', 'm7', 'tritone']
    
    # Select random interval
    interval = random.choice(intervals)
    
    # Generate audio for the interval
    audio_file = generate_interval_audio(interval)
    
    # Create multiple choice options
    options = generate_interval_options(interval, intervals)
    
    return {
        'type': 'interval',
        'audio_file': audio_file,
        'correct_answer': interval,
        'options': options,
        'difficulty': difficulty
    }


def calculate_ear_training_progress():
    """Calculate progress in ear training exercises"""
    results = get_ear_training_results(days=30)
    
    progress = {}
    for exercise_type in ['interval', 'chord', 'melody']:
        type_results = [r for r in results if r.exercise.type == exercise_type]
        
        if type_results:
            accuracy = sum(1 for r in type_results if r.correct) / len(type_results)
            avg_response_time = sum(r.response_time for r in type_results) / len(type_results)
            
            progress[exercise_type] = {
                'accuracy': accuracy,
                'avg_response_time': avg_response_time,
                'total_attempts': len(type_results)
            }
    
    return progress
```

### Chord Progression Matcher
```python
def find_songs_with_progression(progression_id):
    """Find songs that use a specific chord progression"""
    progression = get_chord_progression(progression_id)
    
    # Search for songs with matching progression
    matching_songs = []
    all_songs = get_all_songs()
    
    for song in all_songs:
        if progression_matches(song.chord_progression, progression.progression):
            matching_songs.append(song)
    
    return matching_songs


def progression_matches(song_progression, target_progression):
    """Check if a song's progression matches the target"""
    # Normalize both progressions (convert to same key, etc.)
    normalized_song = normalize_progression(song_progression)
    normalized_target = normalize_progression(target_progression)
    
    # Check for exact match or common variations
    return normalized_song == normalized_target or is_common_variation(normalized_song, normalized_target)
```

### Progress Calculation
```python
def calculate_progress():
    """Calculate user progress across all categories"""
    progress = {}
    
    for category in ['scales', 'arpeggios', 'rhythm', 'technique']:
        # Get completed exercises in this category
        completed = get_completed_exercises(category)
        total = get_total_exercises(category)
        
        # Calculate completion rate
        completion_rate = (len(completed) / total) * 100 if total > 0 else 0
        
        # Calculate average difficulty completed
        avg_difficulty = sum(ex.difficulty for ex in completed) / len(completed) if completed else 0
        
        progress[category] = {
            'completion_rate': completion_rate,
            'average_difficulty': avg_difficulty,
            'exercises_completed': len(completed)
        }
    
    # Add ear training progress
    ear_progress = calculate_ear_training_progress()
    progress['ear_training'] = ear_progress
    
    # Add song practice progress
    song_progress = calculate_song_progress()
    progress['songs'] = song_progress
    
    return progress


def calculate_song_progress():
    """Calculate progress in song practice"""
    all_songs = get_user_songs()
    
    if not all_songs:
        return {'total_songs': 0, 'mastered_songs': 0, 'learning_songs': 0}
    
    mastered = len([s for s in all_songs if s.mastery_level >= 4])
    learning = len([s for s in all_songs if 1 <= s.mastery_level <= 3])
    
    return {
        'total_songs': len(all_songs),
        'mastered_songs': mastered,
        'learning_songs': learning,
        'mastery_percentage': (mastered / len(all_songs)) * 100
    }
```

## Exercise Categories

### Scales (15 exercises)
- Major pentatonic (5 positions)
- Minor pentatonic (5 positions)
- Major scale (3 positions)
- Natural minor scale (3 positions)
- Blues scale (2 positions)

### Arpeggios (10 exercises)
- Major triad arpeggios (3 positions)
- Minor triad arpeggios (3 positions)
- Seventh chord arpeggios (4 types)

### Rhythm (15 exercises)
- Basic rock patterns (5)
- Funk grooves (3)
- Blues shuffle (3)
- Jazz walking bass (2)
- Latin patterns (2)

### Technique (10 exercises)
- Finger independence (3)
- String crossing (2)
- Hammer-ons/pull-offs (2)
- Slap/pop basics (2)
- Raking technique (1)

### Ear Training (20 exercises)
- **Interval Recognition** (10): Perfect 4th, Major 3rd, Minor 3rd, Perfect 5th, etc.
- **Chord Quality** (6): Major, Minor, Diminished, Augmented, 7th chords
- **Melody Playback** (4): Simple 4-8 note melodies for transcription

### Song Practice
- User-added songs with bass tabs
- Difficulty-based categorization
- Genre organization
- Mastery tracking

### Chord Progressions (15 progressions)
- **Basic**: I-IV-V, I-V-vi-IV
- **Jazz**: ii-V-I, iii-vi-ii-V-I
- **Blues**: 12-bar blues variations
- **Pop**: Common pop progressions
- **Funk**: Typical funk progressions

## Installation & Setup

### Requirements
```txt
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
WTForms==3.0.1
python-dotenv==1.0.0
pathlib
```

### Setup Steps
1. Create virtual environment
2. Install requirements
3. Initialize database
4. Add exercise data
5. Run the app

### Running the App
```bash
python run.py
# Opens at http://localhost:5000
```

## Success Metrics
- Daily practice completion rate
- Time spent practicing
- Skill progression in different areas
- User satisfaction with generated sessions

## Future Enhancements
- Backing track library with genre-specific tracks
- Video tutorial integration for exercise examples
- Tempo tracking and improvement metrics
- Practice journal with mood tracking
- Custom exercise builder for user-defined routines
- Bass tuner integration using Web Audio API
- Import/export practice data
- Mobile app development