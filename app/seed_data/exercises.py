from ..models import db, Exercise

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
        # ... and all the others (I will truncate for space in thought but implementation must be complete)
        # Actually I must be precise. Let's add them all.
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
