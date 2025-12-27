"""
Seed data for Bass Practice application.
Contains initial exercises, chord progressions, and ear training exercises.
"""
from .models import db, Exercise, ChordProgression, EarTrainingExercise, Progress, PracticeStreak


def seed_database():
    """Seed the database with initial data if empty."""
    # Check if already seeded
    if Exercise.query.first():
        return
    
    # Seed exercises
    seed_exercises()
    
    # Seed chord progressions
    seed_chord_progressions()
    
    # Note: Ear training exercises are now dynamically generated, not seeded
    
    # Initialize progress tracking for each category
    seed_progress()
    
    # Initialize practice streak
    if not PracticeStreak.query.first():
        streak = PracticeStreak()
        db.session.add(streak)
    
    db.session.commit()


def seed_exercises():
    """Seed initial exercises."""
    exercises = [
        # =================================================================
        # SCALES (15 exercises)
        # =================================================================
        # Major Pentatonic
        Exercise(
            title="Major Pentatonic Scale - Position 1",
            description="Learn the first position of the major pentatonic scale, starting from the root note on the E string.",
            category="scales",
            subcategory="pentatonic",
            difficulty_level=1,
            estimated_duration=5,
            instructions="1. Start on the root note (E string)\n2. Follow the pattern: Root-2-3-5-6\n3. Ascend and descend slowly\n4. Use alternating fingers (index-middle)\n5. Practice with metronome at 60 BPM",
            tips="Keep your fretting hand relaxed. Focus on clean note transitions."
        ),
        Exercise(
            title="Major Pentatonic Scale - Position 2",
            description="Second position of the major pentatonic scale, connecting to position 1.",
            category="scales",
            subcategory="pentatonic",
            difficulty_level=2,
            estimated_duration=5,
            instructions="1. Start from the 2nd degree of the scale\n2. Practice shifting between position 1 and 2\n3. Use a metronome at 70 BPM",
            tips="Practice the connection between positions slowly."
        ),
        Exercise(
            title="Major Pentatonic Scale - All Positions",
            description="Connect all five positions of the major pentatonic scale across the fretboard.",
            category="scales",
            subcategory="pentatonic",
            difficulty_level=4,
            estimated_duration=8,
            instructions="1. Start in position 1\n2. Ascend through all positions\n3. Descend back to position 1\n4. Practice in multiple keys",
            tips="Visualize the entire fretboard pattern."
        ),
        # Minor Pentatonic
        Exercise(
            title="Minor Pentatonic Scale - Position 1",
            description="The most common bass scale pattern - minor pentatonic position 1.",
            category="scales",
            subcategory="pentatonic",
            difficulty_level=1,
            estimated_duration=5,
            instructions="1. Root note on E string\n2. Pattern: Root-b3-4-5-b7\n3. This is the 'blues box' position\n4. Practice at 60 BPM",
            tips="This is the most used scale in rock and blues bass."
        ),
        Exercise(
            title="Minor Pentatonic Scale - Position 2",
            description="Second position of the minor pentatonic scale.",
            category="scales",
            subcategory="pentatonic",
            difficulty_level=2,
            estimated_duration=5,
            instructions="1. Start from the b3 degree\n2. Connect smoothly to position 1\n3. Practice transitions",
            tips="This position is great for fills and runs."
        ),
        # Major Scale
        Exercise(
            title="Major Scale - Two Octaves",
            description="Play the major scale across two octaves using proper fingering.",
            category="scales",
            subcategory="major",
            difficulty_level=3,
            estimated_duration=6,
            instructions="1. Start on the E string root\n2. Use one-finger-per-fret technique\n3. Extend to the second octave\n4. Practice ascending and descending",
            tips="This scale is the foundation of Western music theory."
        ),
        Exercise(
            title="Major Scale - Three Note Per String",
            description="Practice the major scale using three notes per string for speed development.",
            category="scales",
            subcategory="major",
            difficulty_level=5,
            estimated_duration=7,
            instructions="1. Use three notes on each string\n2. This requires position shifts\n3. Great for developing speed\n4. Practice with metronome",
            tips="This technique is used for fast scalar runs."
        ),
        # Natural Minor
        Exercise(
            title="Natural Minor Scale - Basic Pattern",
            description="Learn the natural minor scale pattern starting from the root.",
            category="scales",
            subcategory="minor",
            difficulty_level=2,
            estimated_duration=5,
            instructions="1. Pattern: 1-2-b3-4-5-b6-b7\n2. Compare to major scale\n3. Notice the flatted 3rd, 6th, and 7th",
            tips="This is the relative minor to every major key."
        ),
        Exercise(
            title="Natural Minor Scale - Full Fretboard",
            description="Play the natural minor scale across the entire fretboard.",
            category="scales",
            subcategory="minor",
            difficulty_level=5,
            estimated_duration=8,
            instructions="1. Learn all positions\n2. Connect positions smoothly\n3. Practice in different keys",
            tips="Knowing the full fretboard opens up creative possibilities."
        ),
        # Blues Scale
        Exercise(
            title="Blues Scale - Basic Pattern",
            description="The essential blues scale with the characteristic 'blue note'.",
            category="scales",
            subcategory="blues",
            difficulty_level=2,
            estimated_duration=5,
            instructions="1. Minor pentatonic + b5 (blue note)\n2. Pattern: 1-b3-4-b5-5-b7\n3. Practice bending into the blue note",
            tips="The b5 creates the classic blues sound."
        ),
        Exercise(
            title="Blues Scale - Extended Pattern",
            description="Extended blues scale covering two octaves with variations.",
            category="scales",
            subcategory="blues",
            difficulty_level=4,
            estimated_duration=7,
            instructions="1. Extend across two octaves\n2. Add chromatic approach notes\n3. Practice with blues backing track",
            tips="Use slides and hammer-ons for authentic blues feel."
        ),
        # Modes
        Exercise(
            title="Dorian Mode - Jazz Essential",
            description="The Dorian mode - essential for jazz and funk bass lines.",
            category="scales",
            subcategory="modes",
            difficulty_level=4,
            estimated_duration=6,
            instructions="1. Natural minor with raised 6th\n2. Pattern: 1-2-b3-4-5-6-b7\n3. Great for minor 7th chords",
            tips="This is the most common mode in jazz and fusion."
        ),
        Exercise(
            title="Mixolydian Mode - Dominant Sound",
            description="The Mixolydian mode for dominant 7th chords and rock/blues.",
            category="scales",
            subcategory="modes",
            difficulty_level=4,
            estimated_duration=6,
            instructions="1. Major scale with flatted 7th\n2. Pattern: 1-2-3-4-5-6-b7\n3. Used over dominant 7th chords",
            tips="Essential for blues, rock, and funk."
        ),
        Exercise(
            title="Chromatic Scale Exercise",
            description="Chromatic scale for finger independence and fretboard knowledge.",
            category="scales",
            subcategory="chromatic",
            difficulty_level=2,
            estimated_duration=5,
            instructions="1. Play every fret in sequence\n2. Use all four fingers\n3. Practice one-finger-per-fret\n4. Great warm-up exercise",
            tips="Perfect for warming up and building finger strength."
        ),
        Exercise(
            title="Scale Sequence - Thirds",
            description="Practice scales in thirds for melodic bass line development.",
            category="scales",
            subcategory="sequences",
            difficulty_level=5,
            estimated_duration=7,
            instructions="1. Play scale in thirds (1-3, 2-4, 3-5...)\n2. Ascending and descending\n3. Apply to multiple scales",
            tips="This technique creates more musical bass lines."
        ),
        
        # =================================================================
        # ARPEGGIOS (10 exercises)
        # =================================================================
        Exercise(
            title="Major Triad Arpeggio - Root Position",
            description="Basic major triad arpeggio starting from the root.",
            category="arpeggios",
            subcategory="triads",
            difficulty_level=2,
            estimated_duration=4,
            instructions="1. Pattern: Root-3-5\n2. Practice in all 12 keys\n3. Use different fingerings\n4. Connect across strings",
            tips="Arpeggios outline the chord tones - essential for bass!"
        ),
        Exercise(
            title="Minor Triad Arpeggio - Root Position",
            description="Basic minor triad arpeggio starting from the root.",
            category="arpeggios",
            subcategory="triads",
            difficulty_level=2,
            estimated_duration=4,
            instructions="1. Pattern: Root-b3-5\n2. Compare to major triad\n3. Notice the minor 3rd interval",
            tips="The b3 gives the minor quality."
        ),
        Exercise(
            title="Major Triad Inversions",
            description="Learn all inversions of the major triad.",
            category="arpeggios",
            subcategory="triads",
            difficulty_level=4,
            estimated_duration=6,
            instructions="1. Root position: 1-3-5\n2. First inversion: 3-5-1\n3. Second inversion: 5-1-3\n4. Practice connecting inversions",
            tips="Inversions allow smooth voice leading."
        ),
        Exercise(
            title="Minor Triad Inversions",
            description="Learn all inversions of the minor triad.",
            category="arpeggios",
            subcategory="triads",
            difficulty_level=4,
            estimated_duration=6,
            instructions="1. Root position: 1-b3-5\n2. First inversion: b3-5-1\n3. Second inversion: 5-1-b3",
            tips="Practice connecting to major triad inversions."
        ),
        Exercise(
            title="Major 7th Arpeggio",
            description="Four-note major 7th chord arpeggio.",
            category="arpeggios",
            subcategory="seventh",
            difficulty_level=4,
            estimated_duration=5,
            instructions="1. Pattern: 1-3-5-7\n2. The 7th is a major 7th (half step below root)\n3. Jazz essential chord",
            tips="This chord has a bright, sophisticated sound."
        ),
        Exercise(
            title="Minor 7th Arpeggio",
            description="Four-note minor 7th chord arpeggio.",
            category="arpeggios",
            subcategory="seventh",
            difficulty_level=4,
            estimated_duration=5,
            instructions="1. Pattern: 1-b3-5-b7\n2. Most common jazz chord type\n3. Practice in all keys",
            tips="This is the ii chord in major key progressions."
        ),
        Exercise(
            title="Dominant 7th Arpeggio",
            description="Four-note dominant 7th chord arpeggio.",
            category="arpeggios",
            subcategory="seventh",
            difficulty_level=4,
            estimated_duration=5,
            instructions="1. Pattern: 1-3-5-b7\n2. Creates tension needing resolution\n3. Essential for blues and jazz",
            tips="The tritone between 3 and b7 creates the dominant sound."
        ),
        Exercise(
            title="Diminished 7th Arpeggio",
            description="Four-note diminished 7th chord arpeggio.",
            category="arpeggios",
            subcategory="seventh",
            difficulty_level=5,
            estimated_duration=5,
            instructions="1. Pattern: 1-b3-b5-bb7\n2. Symmetrical - same shape every 3 frets\n3. Used for passing tones",
            tips="Great for creating tension and movement."
        ),
        Exercise(
            title="Arpeggio Across Strings",
            description="Practice arpeggios using all four strings.",
            category="arpeggios",
            subcategory="extended",
            difficulty_level=5,
            estimated_duration=6,
            instructions="1. Spread arpeggio across all strings\n2. Two octave range\n3. Practice position shifts",
            tips="This technique is great for fills and solos."
        ),
        Exercise(
            title="Arpeggio Speed Drill",
            description="Build speed with arpeggio patterns.",
            category="arpeggios",
            subcategory="technique",
            difficulty_level=6,
            estimated_duration=7,
            instructions="1. Start at 60 BPM\n2. Play 16th notes\n3. Gradually increase tempo\n4. Maintain clean articulation",
            tips="Speed comes from relaxation, not tension."
        ),
        
        # =================================================================
        # RHYTHM (15 exercises)
        # =================================================================
        Exercise(
            title="Basic Rock - Eighth Notes",
            description="Fundamental rock bass pattern using eighth notes on root notes.",
            category="rhythm",
            subcategory="rock",
            difficulty_level=1,
            estimated_duration=5,
            instructions="1. Play steady eighth notes\n2. Accent beats 1 and 3\n3. Lock in with kick drum\n4. Practice with rock backing track",
            tips="The foundation of rock bass - keep it steady!"
        ),
        Exercise(
            title="Rock with Fifths",
            description="Classic rock pattern alternating between root and fifth.",
            category="rhythm",
            subcategory="rock",
            difficulty_level=2,
            estimated_duration=5,
            instructions="1. Root on beat 1\n2. Fifth on beat 3\n3. Fill with eighth notes\n4. This is the classic rock sound",
            tips="AC/DC, Led Zeppelin - all use this pattern."
        ),
        Exercise(
            title="Driving Rock - Sixteenth Notes",
            description="Intense rock pattern using sixteenth notes for energy.",
            category="rhythm",
            subcategory="rock",
            difficulty_level=4,
            estimated_duration=6,
            instructions="1. Sixteenth notes on root\n2. Accent every beat\n3. Build endurance\n4. Great for high-energy sections",
            tips="Stamina is key - stay relaxed."
        ),
        Exercise(
            title="Rock Fill Pattern",
            description="Common rock bass fill leading to the next section.",
            category="rhythm",
            subcategory="rock",
            difficulty_level=3,
            estimated_duration=5,
            instructions="1. Ascending scale run on beat 4\n2. Land on the 1 of next bar\n3. Practice leading into chorus",
            tips="Fills signal changes - be intentional."
        ),
        Exercise(
            title="Power Ballad Pattern",
            description="Slow, powerful pattern for rock ballads.",
            category="rhythm",
            subcategory="rock",
            difficulty_level=2,
            estimated_duration=5,
            instructions="1. Whole notes and half notes\n2. Focus on tone and sustain\n3. Let notes ring\n4. Emotional playing",
            tips="Less is more in ballads."
        ),
        # Funk
        Exercise(
            title="Basic Funk - Syncopation",
            description="Introduction to funk syncopation and ghost notes.",
            category="rhythm",
            subcategory="funk",
            difficulty_level=3,
            estimated_duration=6,
            instructions="1. Emphasize the 'and' of beats\n2. Add ghost notes (muted notes)\n3. Lock with snare drum\n4. Practice with funk track",
            tips="Funk is all about the groove - feel it!"
        ),
        Exercise(
            title="Slap Bass - Basic Pop",
            description="Introduction to slap bass technique - the pop.",
            category="rhythm",
            subcategory="funk",
            difficulty_level=4,
            estimated_duration=7,
            instructions="1. Hook finger under G string\n2. Pull and release\n3. Aim for clean, percussive sound\n4. Alternate thumb slap and pop",
            tips="The motion comes from the wrist, not the arm."
        ),
        Exercise(
            title="Funk Octave Pattern",
            description="Classic funk pattern using octaves.",
            category="rhythm",
            subcategory="funk",
            difficulty_level=4,
            estimated_duration=6,
            instructions="1. Root note on E string\n2. Octave on D string\n3. Syncopated rhythm\n4. Add ghost notes between",
            tips="This is the Bootsy Collins sound!"
        ),
        # Blues
        Exercise(
            title="12-Bar Blues - Basic",
            description="The fundamental 12-bar blues bass pattern.",
            category="rhythm",
            subcategory="blues",
            difficulty_level=2,
            estimated_duration=6,
            instructions="1. 4 bars of I chord\n2. 2 bars of IV chord\n3. 2 bars of I chord\n4. V-IV-I-V turnaround\n5. Root-fifth pattern",
            tips="Know this pattern - it's everywhere in music!"
        ),
        Exercise(
            title="Blues Shuffle",
            description="Swung eighth note pattern for blues shuffle feel.",
            category="rhythm",
            subcategory="blues",
            difficulty_level=3,
            estimated_duration=6,
            instructions="1. Swing the eighth notes (long-short)\n2. Root-fifth pattern\n3. Add the 6th for variation\n4. Practice with shuffle backing track",
            tips="The shuffle feel is triplet-based."
        ),
        Exercise(
            title="Blues Turnaround",
            description="Classic blues turnaround in the last two bars.",
            category="rhythm",
            subcategory="blues",
            difficulty_level=3,
            estimated_duration=5,
            instructions="1. Chromatic walk-down\n2. V chord on beat 4\n3. Sets up the next chorus\n4. Multiple variations to learn",
            tips="The turnaround signals the loop - nail it!"
        ),
        # Jazz
        Exercise(
            title="Walking Bass - Basics",
            description="Introduction to jazz walking bass technique.",
            category="rhythm",
            subcategory="jazz",
            difficulty_level=4,
            estimated_duration=7,
            instructions="1. Quarter notes on each beat\n2. Chord tones on strong beats\n3. Passing tones on weak beats\n4. Approach notes to next chord",
            tips="Walking bass is like composing in real-time."
        ),
        Exercise(
            title="Walking Bass - ii-V-I",
            description="Walking bass over the most common jazz progression.",
            category="rhythm",
            subcategory="jazz",
            difficulty_level=5,
            estimated_duration=7,
            instructions="1. Dm7 - G7 - Cmaj7\n2. Use chord tones\n3. Chromatic approach notes\n4. Create melodic lines",
            tips="ii-V-I is the foundation of jazz harmony."
        ),
        # Latin
        Exercise(
            title="Bossa Nova Pattern",
            description="Classic Brazilian bossa nova bass pattern.",
            category="rhythm",
            subcategory="latin",
            difficulty_level=3,
            estimated_duration=5,
            instructions="1. Root on beat 1\n2. Fifth on the 'and' of 2\n3. Smooth, flowing feel\n4. Think 'The Girl from Ipanema'",
            tips="Bossa nova is gentle and flowing."
        ),
        Exercise(
            title="Samba Bass Pattern",
            description="Energetic Brazilian samba bass pattern.",
            category="rhythm",
            subcategory="latin",
            difficulty_level=4,
            estimated_duration=6,
            instructions="1. Syncopated sixteenth note pattern\n2. Strong accent on beat 2\n3. High energy, driving feel\n4. Practice with samba drums",
            tips="Samba is intense - build your stamina!"
        ),
        
        # =================================================================
        # TECHNIQUE (10 exercises)
        # =================================================================
        Exercise(
            title="Finger Independence - Spider Exercise",
            description="Classic spider exercise for building finger independence.",
            category="technique",
            subcategory="finger_strength",
            difficulty_level=2,
            estimated_duration=5,
            instructions="1. One finger per fret (1-2-3-4)\n2. Move across all strings\n3. Keep unused fingers down\n4. Start slow, build speed",
            tips="This builds the foundation for all bass playing."
        ),
        Exercise(
            title="Finger Independence - Reverse Spider",
            description="Spider exercise in reverse for balanced development.",
            category="technique",
            subcategory="finger_strength",
            difficulty_level=3,
            estimated_duration=5,
            instructions="1. Pattern: 4-3-2-1\n2. Move across strings\n3. Develops pinky strength\n4. Balance with regular spider",
            tips="The pinky often needs extra work."
        ),
        Exercise(
            title="Finger Permutations",
            description="All 24 permutations of four-finger patterns.",
            category="technique",
            subcategory="finger_strength",
            difficulty_level=5,
            estimated_duration=8,
            instructions="1. 1234, 1243, 1324, 1342...\n2. Practice each permutation\n3. Identifies weak finger combinations\n4. Ultimate finger independence",
            tips="This reveals your weak spots."
        ),
        Exercise(
            title="String Crossing - Adjacent Strings",
            description="Smooth string crossing between adjacent strings.",
            category="technique",
            subcategory="string_crossing",
            difficulty_level=2,
            estimated_duration=5,
            instructions="1. Alternate between E and A strings\n2. Alternate between A and D strings\n3. Keep motion minimal\n4. No unwanted string noise",
            tips="Efficient movement is key."
        ),
        Exercise(
            title="String Crossing - Skip String",
            description="String crossing skipping one string (E to D, A to G).",
            category="technique",
            subcategory="string_crossing",
            difficulty_level=4,
            estimated_duration=6,
            instructions="1. E string to D string\n2. A string to G string\n3. Mute skipped string\n4. Common in arpeggios",
            tips="Muting is crucial for clean sound."
        ),
        Exercise(
            title="Hammer-Ons and Pull-Offs",
            description="Legato technique for smooth, connected notes.",
            category="technique",
            subcategory="legato",
            difficulty_level=3,
            estimated_duration=5,
            instructions="1. Hammer-on: strike string without picking\n2. Pull-off: pluck string with fretting finger\n3. Practice scales with legato\n4. Build finger strength",
            tips="The fretting hand does the work."
        ),
        Exercise(
            title="Slides and Position Shifts",
            description="Smooth slides and position shifts across the fretboard.",
            category="technique",
            subcategory="slides",
            difficulty_level=3,
            estimated_duration=5,
            instructions="1. Slide into notes\n2. Slide out of notes\n3. Position shifts during slides\n4. Maintain consistent pressure",
            tips="Slides add expression and smoothness."
        ),
        Exercise(
            title="Right Hand Technique - Alternating",
            description="Consistent alternating finger technique.",
            category="technique",
            subcategory="right_hand",
            difficulty_level=2,
            estimated_duration=5,
            instructions="1. Strict alternation: index-middle\n2. Even volume on both fingers\n3. Consistent tone\n4. Practice with metronome",
            tips="The right hand is often neglected - don't skip this!"
        ),
        Exercise(
            title="Muting Technique",
            description="Left and right hand muting for clean playing.",
            category="technique",
            subcategory="muting",
            difficulty_level=3,
            estimated_duration=5,
            instructions="1. Left hand: lift finger slightly after note\n2. Right hand: rest thumb on lower strings\n3. Palm muting for specific effects\n4. Clean stops without ringing",
            tips="Great bassists are great at muting."
        ),
        Exercise(
            title="Speed Building Exercise",
            description="Systematic speed development with metronome.",
            category="technique",
            subcategory="speed",
            difficulty_level=5,
            estimated_duration=7,
            instructions="1. Start at comfortable tempo\n2. Play 1 minute perfectly\n3. Increase 5 BPM\n4. If mistakes, go back 10 BPM\n5. Build gradually over weeks",
            tips="Speed is a byproduct of accuracy."
        ),
        
        # =================================================================
        # THEORY (5 exercises)
        # =================================================================
        Exercise(
            title="Circle of Fifths Navigation",
            description="Navigate the circle of fifths on the bass.",
            category="theory",
            subcategory="harmony",
            difficulty_level=3,
            estimated_duration=6,
            instructions="1. Start on C\n2. Move up a fifth to G\n3. Continue: D, A, E, B, F#, C#, Ab, Eb, Bb, F, C\n4. Visualize on fretboard",
            tips="The circle of fifths is the key to understanding music."
        ),
        Exercise(
            title="Chord Tone Targeting",
            description="Practice hitting chord tones over changes.",
            category="theory",
            subcategory="harmony",
            difficulty_level=4,
            estimated_duration=6,
            instructions="1. Play root on beat 1\n2. Add 3rd and 5th\n3. Practice over simple changes\n4. Outline the harmony",
            tips="Chord tones are your safe notes."
        ),
        Exercise(
            title="Interval Recognition - Playing",
            description="Play and identify intervals on the bass.",
            category="theory",
            subcategory="intervals",
            difficulty_level=3,
            estimated_duration=5,
            instructions="1. Play each interval from the same root\n2. Sing the interval\n3. Recognize the sound\n4. m2, M2, m3, M3, P4, tritone, P5, m6, M6, m7, M7, P8",
            tips="Knowing intervals transforms your playing."
        ),
        Exercise(
            title="Scale Degree Awareness",
            description="Play scales while thinking of scale degrees.",
            category="theory",
            subcategory="scales",
            difficulty_level=3,
            estimated_duration=5,
            instructions="1. Play major scale\n2. Say degree number aloud (1, 2, 3...)\n3. Random degree jumps\n4. Apply to other scales",
            tips="Think in numbers, not just patterns."
        ),
        Exercise(
            title="Chord Progression Practice",
            description="Practice common chord progressions.",
            category="theory",
            subcategory="harmony",
            difficulty_level=4,
            estimated_duration=6,
            instructions="1. I-IV-V progression\n2. ii-V-I progression\n3. I-vi-IV-V progression\n4. Play roots, then add chord tones",
            tips="These progressions are everywhere in music."
        ),
    ]
    
    for exercise in exercises:
        db.session.add(exercise)
    
    db.session.commit()


def seed_chord_progressions():
    """Seed chord progressions."""
    progressions = [
        ChordProgression(
            name="I-IV-V (Basic Rock)",
            numerals="I-IV-V",
            progression='["C", "F", "G"]',
            genre="rock",
            difficulty_level=1,
            description="The most fundamental rock and blues progression. Used in countless songs.",
            bass_line_examples='["Root notes on each chord", "Root-fifth pattern", "Walking eighth notes"]',
            common_songs="La Bamba, Twist and Shout, Wild Thing"
        ),
        ChordProgression(
            name="I-V-vi-IV (Pop)",
            numerals="I-V-vi-IV",
            progression='["C", "G", "Am", "F"]',
            genre="pop",
            difficulty_level=2,
            description="The most popular chord progression in modern pop music.",
            bass_line_examples='["Root notes", "Root-fifth", "Add passing tones"]',
            common_songs="Let It Be, No Woman No Cry, With or Without You"
        ),
        ChordProgression(
            name="ii-V-I (Jazz)",
            numerals="ii-V-I",
            progression='["Dm7", "G7", "Cmaj7"]',
            genre="jazz",
            difficulty_level=4,
            description="The fundamental jazz progression. Master this for jazz bass.",
            bass_line_examples='["Walking bass quarters", "Chord tones on beats 1 and 3", "Chromatic approach"]',
            common_songs="Autumn Leaves, All The Things You Are, Fly Me to the Moon"
        ),
        ChordProgression(
            name="12-Bar Blues",
            numerals="I-I-I-I-IV-IV-I-I-V-IV-I-V",
            progression='["C7", "C7", "C7", "C7", "F7", "F7", "C7", "C7", "G7", "F7", "C7", "G7"]',
            genre="blues",
            difficulty_level=2,
            description="The foundation of blues and rock music. Essential for any bassist.",
            bass_line_examples='["Root-fifth shuffle", "Walking blues line", "Chromatic turnaround"]',
            common_songs="Johnny B. Goode, Sweet Home Chicago, The Thrill Is Gone"
        ),
        ChordProgression(
            name="I-vi-IV-V (50s)",
            numerals="I-vi-IV-V",
            progression='["C", "Am", "F", "G"]',
            genre="pop",
            difficulty_level=1,
            description="Classic 1950s doo-wop progression. Still used today.",
            bass_line_examples='["Root notes", "Arpeggiated pattern", "Walking line"]',
            common_songs="Stand By Me, Earth Angel, Every Breath You Take"
        ),
        ChordProgression(
            name="i-bVII-bVI-V (Minor)",
            numerals="i-bVII-bVI-V",
            progression='["Am", "G", "F", "E"]',
            genre="rock",
            difficulty_level=3,
            description="Dramatic minor key progression used in rock and metal.",
            bass_line_examples='["Power root notes", "Descending line", "Add chromatic walk"]',
            common_songs="Stairway to Heaven, All Along the Watchtower, Hit the Road Jack"
        ),
        ChordProgression(
            name="I-bVII-IV (Rock)",
            numerals="I-bVII-IV",
            progression='["C", "Bb", "F"]',
            genre="rock",
            difficulty_level=2,
            description="Classic rock progression with the flat 7th chord.",
            bass_line_examples='["Driving eighth notes", "Root-fifth", "Syncopated pattern"]',
            common_songs="Sweet Child O Mine, Born to Be Wild, You Really Got Me"
        ),
        ChordProgression(
            name="iii-vi-ii-V-I (Jazz Turnaround)",
            numerals="iii-vi-ii-V-I",
            progression='["Em7", "Am7", "Dm7", "G7", "Cmaj7"]',
            genre="jazz",
            difficulty_level=5,
            description="Extended jazz turnaround. Advanced walking bass territory.",
            bass_line_examples='["Walking quarters", "Chord scales", "Tritone subs"]',
            common_songs="I Got Rhythm, Rhythm Changes, Oleo"
        ),
        ChordProgression(
            name="i-iv-v (Minor Blues)",
            numerals="i-iv-v",
            progression='["Am", "Dm", "Em"]',
            genre="blues",
            difficulty_level=2,
            description="Minor blues progression for darker, moodier songs.",
            bass_line_examples='["Minor pentatonic fills", "Root-fifth", "Chromatic approaches"]',
            common_songs="The Thrill Is Gone, Black Magic Woman"
        ),
        ChordProgression(
            name="I-IV (Funk Vamp)",
            numerals="I-IV",
            progression='["C7", "F7"]',
            genre="funk",
            difficulty_level=3,
            description="Two-chord funk vamp. All about the groove!",
            bass_line_examples='["Syncopated sixteenths", "Octave pattern", "Ghost notes"]',
            common_songs="Superstition, Chameleon, Pick Up the Pieces"
        ),
        ChordProgression(
            name="I-V-vi-iii-IV-I-IV-V (Canon)",
            numerals="I-V-vi-iii-IV-I-IV-V",
            progression='["C", "G", "Am", "Em", "F", "C", "F", "G"]',
            genre="pop",
            difficulty_level=3,
            description="Pachelbel's Canon progression. Surprisingly common in pop.",
            bass_line_examples='["Descending bass line", "Root notes", "Add passing tones"]',
            common_songs="Graduation, Basket Case, Blues Traveler"
        ),
        ChordProgression(
            name="i-bVI-bIII-bVII (Andalusian)",
            numerals="i-bVI-bIII-bVII",
            progression='["Am", "F", "C", "G"]',
            genre="flamenco",
            difficulty_level=3,
            description="The Andalusian cadence. Spanish and Middle Eastern flavor.",
            bass_line_examples='["Descending pattern", "Flamenco rhythm", "Dramatic accents"]',
            common_songs="Hit the Road Jack, Sultans of Swing"
        ),
        ChordProgression(
            name="ii-V (Jazz Turnaround Short)",
            numerals="ii-V",
            progression='["Dm7", "G7"]',
            genre="jazz",
            difficulty_level=4,
            description="Short jazz turnaround, often repeated.",
            bass_line_examples='["Walking quarter notes", "Chromatic approach to V", "Guide tones"]',
            common_songs="Common in jazz standards"
        ),
        ChordProgression(
            name="I-I-I-I (One Chord Groove)",
            numerals="I",
            progression='["E7"]',
            genre="funk",
            difficulty_level=2,
            description="One chord vamp - all about rhythm and groove.",
            bass_line_examples='["Syncopated pattern", "Slap groove", "Modal exploration"]',
            common_songs="Brick House, Thank You, Good Times"
        ),
        ChordProgression(
            name="I-bIII-bVII-IV (Mixolydian)",
            numerals="I-bIII-bVII-IV",
            progression='["C", "Eb", "Bb", "F"]',
            genre="rock",
            difficulty_level=3,
            description="Uses notes from Mixolydian mode. Great for jam bands.",
            bass_line_examples='["Modal bass line", "Mixolydian runs", "Pedal tone"]',
            common_songs="Hey Joe, The Wind Cries Mary"
        ),
    ]
    
    for progression in progressions:
        db.session.add(progression)
    
    db.session.commit()


def seed_ear_training_exercises():
    """Seed ear training exercises."""
    exercises = [
        # Intervals
        EarTrainingExercise(
            exercise_type="interval",
            title="Minor 2nd (Half Step)",
            description="The smallest interval - one fret on the bass.",
            difficulty_level=1,
            root_note="C",
            correct_answer="m2",
            options='["m2", "M2", "m3", "M3"]',
            hints="Think 'Jaws' theme"
        ),
        EarTrainingExercise(
            exercise_type="interval",
            title="Major 2nd (Whole Step)",
            description="Two frets apart - a whole step.",
            difficulty_level=1,
            root_note="C",
            correct_answer="M2",
            options='["m2", "M2", "m3", "M3"]',
            hints="Think beginning of a major scale"
        ),
        EarTrainingExercise(
            exercise_type="interval",
            title="Minor 3rd",
            description="Three frets - the minor chord interval.",
            difficulty_level=2,
            root_note="C",
            correct_answer="m3",
            options='["m2", "M2", "m3", "M3"]',
            hints="Think 'Greensleeves'"
        ),
        EarTrainingExercise(
            exercise_type="interval",
            title="Major 3rd",
            description="Four frets - the major chord interval.",
            difficulty_level=2,
            root_note="C",
            correct_answer="M3",
            options='["m3", "M3", "P4", "P5"]',
            hints="Think 'Oh When the Saints'"
        ),
        EarTrainingExercise(
            exercise_type="interval",
            title="Perfect 4th",
            description="Five frets - very common bass interval.",
            difficulty_level=1,
            root_note="C",
            correct_answer="P4",
            options='["M3", "P4", "tritone", "P5"]',
            hints="Think 'Here Comes the Bride'"
        ),
        EarTrainingExercise(
            exercise_type="interval",
            title="Tritone (Augmented 4th)",
            description="Six frets - the devil's interval.",
            difficulty_level=3,
            root_note="C",
            correct_answer="tritone",
            options='["P4", "tritone", "P5", "m6"]',
            hints="Think 'The Simpsons' theme"
        ),
        EarTrainingExercise(
            exercise_type="interval",
            title="Perfect 5th",
            description="Seven frets - the power chord interval.",
            difficulty_level=1,
            root_note="C",
            correct_answer="P5",
            options='["P4", "tritone", "P5", "m6"]',
            hints="Think 'Star Wars' theme"
        ),
        EarTrainingExercise(
            exercise_type="interval",
            title="Minor 6th",
            description="Eight frets apart.",
            difficulty_level=3,
            root_note="C",
            correct_answer="m6",
            options='["P5", "m6", "M6", "m7"]',
            hints="Think 'The Entertainer'"
        ),
        EarTrainingExercise(
            exercise_type="interval",
            title="Major 6th",
            description="Nine frets apart.",
            difficulty_level=3,
            root_note="C",
            correct_answer="M6",
            options='["m6", "M6", "m7", "M7"]',
            hints="Think 'NBC theme'"
        ),
        EarTrainingExercise(
            exercise_type="interval",
            title="Minor 7th",
            description="Ten frets - common in dominant chords.",
            difficulty_level=2,
            root_note="C",
            correct_answer="m7",
            options='["M6", "m7", "M7", "P8"]',
            hints="Think 'Somewhere' from West Side Story"
        ),
        # Chord Quality
        EarTrainingExercise(
            exercise_type="chord",
            title="Major Chord",
            description="Identify the bright, happy major chord sound.",
            difficulty_level=1,
            root_note="C",
            correct_answer="major",
            options='["major", "minor", "diminished", "augmented"]',
            hints="Sounds happy and stable"
        ),
        EarTrainingExercise(
            exercise_type="chord",
            title="Minor Chord",
            description="Identify the darker minor chord sound.",
            difficulty_level=1,
            root_note="C",
            correct_answer="minor",
            options='["major", "minor", "diminished", "augmented"]',
            hints="Sounds sad or mysterious"
        ),
        EarTrainingExercise(
            exercise_type="chord",
            title="Diminished Chord",
            description="Identify the tense diminished chord sound.",
            difficulty_level=3,
            root_note="C",
            correct_answer="diminished",
            options='["major", "minor", "diminished", "augmented"]',
            hints="Sounds unstable and tense"
        ),
        EarTrainingExercise(
            exercise_type="chord",
            title="Augmented Chord",
            description="Identify the dreamy augmented chord sound.",
            difficulty_level=3,
            root_note="C",
            correct_answer="augmented",
            options='["major", "minor", "diminished", "augmented"]',
            hints="Sounds like it's floating upward"
        ),
        EarTrainingExercise(
            exercise_type="chord",
            title="Major 7th Chord",
            description="Identify the smooth major 7th chord.",
            difficulty_level=4,
            root_note="C",
            correct_answer="major7",
            options='["major7", "minor7", "dominant7", "diminished7"]',
            hints="Smooth and sophisticated"
        ),
        EarTrainingExercise(
            exercise_type="chord",
            title="Minor 7th Chord",
            description="Identify the mellow minor 7th chord.",
            difficulty_level=4,
            root_note="C",
            correct_answer="minor7",
            options='["major7", "minor7", "dominant7", "diminished7"]',
            hints="Mellow and jazzy"
        ),
        # Melody
        EarTrainingExercise(
            exercise_type="melody",
            title="Simple Major Melody",
            description="Transcribe a simple 4-note major melody.",
            difficulty_level=2,
            root_note="C",
            correct_answer="1-3-5-3",
            options='["1-3-5-3", "1-2-3-2", "1-5-3-1", "1-3-2-1"]',
            hints="Arpeggio-based pattern"
        ),
        EarTrainingExercise(
            exercise_type="melody",
            title="Simple Minor Melody",
            description="Transcribe a simple 4-note minor melody.",
            difficulty_level=2,
            root_note="A",
            correct_answer="1-b3-5-b3",
            options='["1-b3-5-b3", "1-2-b3-2", "1-5-b3-1", "1-b3-4-b3"]',
            hints="Minor arpeggio-based"
        ),
        EarTrainingExercise(
            exercise_type="melody",
            title="Pentatonic Phrase",
            description="Transcribe a pentatonic melody.",
            difficulty_level=3,
            root_note="E",
            correct_answer="1-b3-4-5-b7",
            options='["1-b3-4-5-b7", "1-2-3-5-6", "1-b3-5-b7-1", "1-4-5-b7-1"]',
            hints="Classic blues/rock lick"
        ),
        EarTrainingExercise(
            exercise_type="melody",
            title="Bass Line Phrase",
            description="Transcribe a typical bass line pattern.",
            difficulty_level=4,
            root_note="G",
            correct_answer="1-1-5-5-b7-b7-5",
            options='["1-1-5-5-b7-b7-5", "1-3-5-3-1-5-1", "1-5-1-5-4-5-1", "1-1-3-3-5-5-3"]',
            hints="Root-fifth based pattern"
        ),
    ]
    
    for exercise in exercises:
        db.session.add(exercise)
    
    db.session.commit()


def seed_progress():
    """Initialize progress tracking for each category."""
    categories = ['scales', 'arpeggios', 'rhythm', 'technique', 'theory']
    
    for category in categories:
        if not Progress.query.filter_by(category=category).first():
            progress = Progress(category=category)
            db.session.add(progress)
    
    db.session.commit()
