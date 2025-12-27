# Bass Practice

A local Python web application for bass guitar practice with daily practice generation, progress tracking, ear training, and song management.

## Features

- **Daily Practice Generator**: Automatically generates balanced practice sessions based on your skill level and preferences
- **Exercise Library**: 50+ exercises covering scales, arpeggios, rhythm patterns, technique, and theory
- **Practice Session Interface**: Timer, metronome, and exercise tracking
- **Song Practice Management**: Track songs you're learning with daily playlist generation
- **Chord Progression Library**: Common progressions with bass line examples
- **Ear Training**: Interval and chord recognition exercises
- **Progress Tracking**: Charts, statistics, and streak tracking

## Installation

1. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # macOS/Linux
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python run.py
   ```

4. **Open your browser** to http://localhost:5000

## First Time Setup

1. Go to **Settings** to configure your profile:
   - Set your skill level (1-10)
   - Choose your preferred genre
   - Set your preferred session duration

2. The app will automatically seed the database with:
   - 50+ exercises across all categories
   - 15 common chord progressions
   - 20 ear training exercises

## Usage

### Dashboard
The main dashboard shows:
- Current practice streak
- Today's generated practice session
- Daily song playlist
- Skills progress chart

### Practice Sessions
1. Click "Start Practice Session" to generate a new session
2. Work through each exercise with the built-in timer
3. Mark exercises as complete and rate the difficulty
4. Use the metronome for timing practice

### Song Library
1. Add songs you want to practice
2. The app generates a daily playlist based on:
   - Songs you haven't practiced recently
   - Songs you're currently learning
   - Mastered songs for review
3. Rate your practice quality to track mastery

### Ear Training
Practice interval and chord recognition:
- Intervals: Minor 2nd to Octave
- Chords: Major, minor, diminished, augmented, 7th chords
- Track your accuracy over time

### Progress
View detailed statistics:
- Practice streak and history
- Skills progress by category
- Ear training accuracy
- Song mastery progress

## Project Structure

```
bass_practice/
├── app/
│   ├── __init__.py           # Flask app initialization
│   ├── models.py             # Database models
│   ├── routes.py             # URL routes
│   ├── practice_generator.py # Practice session generation
│   ├── song_manager.py       # Song playlist logic
│   ├── seed_data.py          # Initial data
│   ├── templates/            # HTML templates
│   └── static/               # CSS, JS, audio
├── data/
│   └── bass_practice.db      # SQLite database
├── requirements.txt
├── run.py                    # Entry point
└── README.md
```

## Technologies

- **Backend**: Flask, SQLAlchemy
- **Database**: SQLite
- **Frontend**: Bootstrap 5, Chart.js
- **Audio**: Web Audio API (for metronome and ear training)

## License

MIT License - feel free to use and modify for your own practice!
