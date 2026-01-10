let currentExercise = null;
let exerciseType = window.initialExerciseType || 'interval';
let audioContext = null;
let startTime = null;

// Interval semitones mapping
const intervals = {
    'm2': 1, 'M2': 2, 'm3': 3, 'M3': 4, 'P4': 5,
    'tritone': 6, 'P5': 7, 'm6': 8, 'M6': 9, 'm7': 10, 'M7': 11, 'P8': 12
};

// Chord type to semitones mapping
const chordTypes = {
    'major': [0, 4, 7],
    'minor': [0, 3, 7],
    'diminished': [0, 3, 6],
    'augmented': [0, 4, 8],
    'major7': [0, 4, 7, 11],
    'minor7': [0, 3, 7, 10],
    'dominant7': [0, 4, 7, 10],
    'diminished7': [0, 3, 6, 9]
};

// Scale degree to semitones (for melody exercises)
const scaleDegrees = {
    '1': 0, '2': 2, '3': 4, '4': 5, '5': 7, '6': 9, '7': 11, '8': 12,
    'b2': 1, 'b3': 3, 'b5': 6, 'b6': 8, 'b7': 10,
    '#4': 6, '#5': 8
};

function initAudioContext() {
    if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }
    // Resume if suspended (required for some browsers)
    if (audioContext.state === 'suspended') {
        audioContext.resume();
    }
    return audioContext;
}

function playNote(frequency, duration = 0.5, delay = 0) {
    // Validate frequency
    if (!frequency || !isFinite(frequency) || frequency <= 0) {
        console.error('Invalid frequency:', frequency);
        return;
    }

    const ctx = initAudioContext();
    const startAt = ctx.currentTime + delay;

    const oscillator = ctx.createOscillator();
    const gainNode = ctx.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(ctx.destination);

    oscillator.type = 'sine';
    oscillator.frequency.setValueAtTime(frequency, startAt);

    // Envelope
    gainNode.gain.setValueAtTime(0, startAt);
    gainNode.gain.linearRampToValueAtTime(0.4, startAt + 0.02);
    gainNode.gain.exponentialRampToValueAtTime(0.01, startAt + duration);

    oscillator.start(startAt);
    oscillator.stop(startAt + duration + 0.1);
}

function frequencyFromSemitones(rootFreq, semitones) {
    return rootFreq * Math.pow(2, semitones / 12);
}

function playInterval(rootFreq, semitones) {
    if (semitones === undefined || semitones === null) {
        console.error('Invalid semitones for interval:', semitones);
        return;
    }

    const secondFreq = frequencyFromSemitones(rootFreq, semitones);

    // Play root note
    playNote(rootFreq, 0.6, 0);
    // Play second note after a delay
    playNote(secondFreq, 0.6, 0.7);
}

function playChord(rootFreq, chordType) {
    const semitones = chordTypes[chordType];

    if (!semitones) {
        console.error('Unknown chord type:', chordType);
        return;
    }

    // Play all notes of the chord simultaneously with slight staggering
    semitones.forEach((s, i) => {
        const freq = frequencyFromSemitones(rootFreq, s);
        playNote(freq, 1.2, i * 0.05);
    });
}

function playChordFromSemitones(rootFreq, semitones) {
    // Play chord from array of semitones
    if (!Array.isArray(semitones)) {
        console.error('Invalid semitones array:', semitones);
        return;
    }

    semitones.forEach((s, i) => {
        const freq = frequencyFromSemitones(rootFreq, s);
        playNote(freq, 1.2, i * 0.05);
    });
}

function playMelody(rootFreq, melodyPattern) {
    // Parse melody pattern like "1-3-5-3" or "1-b3-5-b7"
    let pattern = melodyPattern;

    // Handle if it's a string
    if (typeof pattern === 'string') {
        pattern = pattern.split('-').map(p => p.trim());
    }

    if (!Array.isArray(pattern)) {
        console.error('Invalid melody pattern:', melodyPattern);
        return;
    }

    pattern.forEach((degree, i) => {
        const semitones = scaleDegrees[degree];
        if (semitones !== undefined) {
            const freq = frequencyFromSemitones(rootFreq, semitones);
            playNote(freq, 0.4, i * 0.5);
        } else {
            console.warn('Unknown scale degree:', degree);
        }
    });
}

function playMelodyFromSemitones(rootFreq, semitones) {
    // Play melody from array of semitones
    if (!Array.isArray(semitones)) {
        console.error('Invalid semitones array:', semitones);
        return;
    }

    semitones.forEach((s, i) => {
        const freq = frequencyFromSemitones(rootFreq, s);
        playNote(freq, 0.4, i * 0.5);
    });
}

const playSoundBtn = document.getElementById('playSound');
if (playSoundBtn) {
    playSoundBtn.addEventListener('click', function () {
        if (!currentExercise) {
            alert('Please load an exercise first by clicking "New Exercise"');
            return;
        }

        startTime = Date.now();

        // Fetch audio data from server (doesn't reveal the answer)
        fetch(`/ear-training/play/${currentExercise.id}`)
            .then(response => response.json())
            .then(audioData => {
                if (audioData.error) {
                    alert('Cannot play audio for this exercise');
                    return;
                }

                // Use C3 as root frequency (good bass range)
                const rootFreq = 130.81;

                if (audioData.type === 'interval') {
                    playInterval(rootFreq, audioData.semitones);
                } else if (audioData.type === 'chord') {
                    playChordFromSemitones(rootFreq, audioData.semitones);
                } else if (audioData.type === 'melody') {
                    playMelodyFromSemitones(rootFreq, audioData.semitones);
                }
            })
            .catch(err => {
                console.error('Error fetching audio data:', err);
                alert('Error playing audio');
            });
    });
}

const newExerciseBtn = document.getElementById('newExerciseBtn');
if (newExerciseBtn) newExerciseBtn.addEventListener('click', loadNewExercise);

document.querySelectorAll('.exercise-type-btn').forEach(btn => {
    btn.addEventListener('click', function () {
        document.querySelectorAll('.exercise-type-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        exerciseType = this.dataset.type;
        loadNewExercise();
    });
});

function loadNewExercise() {
    fetch(`/ear-training/exercise?type=${exerciseType}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                const title = document.getElementById('exerciseTitle');
                const desc = document.getElementById('exerciseDescription');
                if (title) title.textContent = 'No exercises available';
                if (desc) desc.textContent = 'Try selecting a different exercise type.';
                const optionsArea = document.getElementById('optionsArea');
                if (optionsArea) optionsArea.classList.add('d-none');
                currentExercise = null;
                return;
            }

            currentExercise = data;

            // Update the current level display
            const currentLevel = document.getElementById('currentLevel');
            if (data.difficulty && currentLevel) {
                currentLevel.textContent = data.difficulty;
            }

            // Show generic title/description to avoid revealing the answer
            const typeLabels = {
                'interval': 'Identify the Interval',
                'chord': 'Identify the Chord',
                'melody': 'Identify the Melody'
            };
            const exerciseTitle = document.getElementById('exerciseTitle');
            const exerciseDescription = document.getElementById('exerciseDescription');
            if (exerciseTitle) exerciseTitle.textContent = typeLabels[data.type] || 'Listen and Identify';
            if (exerciseDescription) exerciseDescription.textContent = 'Click "Play Sound" and listen carefully, then select your answer.';

            // Parse options
            let options;
            try {
                options = typeof data.options === 'string' ? JSON.parse(data.options) : data.options;
            } catch (e) {
                console.error('Error parsing options:', e);
                options = [];
            }

            // Ensure options is an array
            if (!Array.isArray(options)) {
                options = [options];
            }

            // Create option buttons
            const optionsArea = document.getElementById('answerOptions');
            if (optionsArea) {
                optionsArea.innerHTML = '';

                options.forEach(opt => {
                    const btn = document.createElement('button');
                    btn.className = 'btn btn-outline-primary btn-lg m-1';
                    btn.textContent = opt;
                    btn.onclick = () => submitAnswer(opt);
                    optionsArea.appendChild(btn);
                });
            }

            const optionsAreaContainer = document.getElementById('optionsArea');
            if (optionsAreaContainer) optionsAreaContainer.classList.remove('d-none');
            const resultArea = document.getElementById('resultArea');
            if (resultArea) resultArea.classList.add('d-none');
        })
        .catch(err => {
            console.error('Error loading exercise:', err);
            const exerciseTitle = document.getElementById('exerciseTitle');
            const exerciseDescription = document.getElementById('exerciseDescription');
            if (exerciseTitle) exerciseTitle.textContent = 'Error loading exercise';
            if (exerciseDescription) exerciseDescription.textContent = 'Please try again.';
        });
}

function submitAnswer(answer) {
    if (!currentExercise) return;

    const responseTime = startTime ? Date.now() - startTime : 0;

    fetch('/ear-training/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            exercise_id: currentExercise.id,
            answer: answer,
            response_time: responseTime
        })
    })
        .then(response => response.json())
        .then(data => {
            const resultArea = document.getElementById('resultArea');
            const resultMessage = document.getElementById('resultMessage');

            if (resultArea) resultArea.classList.remove('d-none');

            // Show hint after answering (educational feedback)
            const hint = currentExercise.hints ? `<br><small class="text-muted">Hint: ${currentExercise.hints}</small>` : '';

            if (resultMessage) {
                if (data.correct) {
                    resultMessage.className = 'alert alert-success';
                    resultMessage.innerHTML = `<i class="bi bi-check-circle-fill"></i> Correct! It was <strong>${data.correct_answer}</strong>${hint}`;
                } else {
                    resultMessage.className = 'alert alert-danger';
                    resultMessage.innerHTML = `<i class="bi bi-x-circle-fill"></i> Incorrect. The answer was: <strong>${data.correct_answer}</strong>${hint}`;
                }
            }

            // Auto-load next exercise after 3 seconds (more time to read hint)
            setTimeout(loadNewExercise, 3000);
        })
        .catch(err => {
            console.error('Error submitting answer:', err);
        });
}

// Load initial exercise when page loads
document.addEventListener('DOMContentLoaded', () => {
    loadNewExercise();
});
