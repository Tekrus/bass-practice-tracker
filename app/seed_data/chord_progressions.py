from ..models import db, ChordProgression

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
