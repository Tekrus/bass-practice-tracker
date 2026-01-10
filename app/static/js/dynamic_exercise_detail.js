// Timer State
let timerSeconds = window.exerciseEstimatedDuration * 60 || 300;
let timerInterval = null;
let timerRunning = false;

// Audio Context and State
let audioContext = null;
let timingRunning = false;
let timingInterval = null;
let currentBeat = 0;
let volume = 0.7;

function updateTimerDisplay() {
    const minutes = Math.floor(timerSeconds / 60);
    const seconds = timerSeconds % 60;
    const display = document.getElementById('timerDisplay');
    if (display) {
        display.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
    }
}

function startTimer() {
    if (!timerRunning && timerSeconds > 0) {
        timerRunning = true;
        timerInterval = setInterval(() => {
            timerSeconds--;
            updateTimerDisplay();
            if (timerSeconds <= 0) {
                pauseTimer();
                alert('Time is up!');
            }
        }, 1000);
    }
}

function pauseTimer() {
    timerRunning = false;
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
}

function resetTimer() {
    pauseTimer();
    timerSeconds = window.exerciseEstimatedDuration * 60 || 300;
    updateTimerDisplay();
}

function initAudioContext() {
    if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (audioContext.state === 'suspended') {
        audioContext.resume();
    }
    return audioContext;
}

// Get current mode (metronome or drums)
function isDrumMode() {
    const drumsRadio = document.getElementById('modeDrums');
    return drumsRadio ? drumsRadio.checked : false;
}

// Metronome click sound
function playClick(accent = false) {
    const ctx = initAudioContext();
    const oscillator = ctx.createOscillator();
    const gainNode = ctx.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(ctx.destination);

    oscillator.frequency.value = accent ? 1200 : 1000;
    oscillator.type = 'square';

    const vol = accent ? 0.4 * volume : 0.3 * volume;
    gainNode.gain.setValueAtTime(vol, ctx.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.05);

    oscillator.start(ctx.currentTime);
    oscillator.stop(ctx.currentTime + 0.05);
}

// Drum synthesis functions
function playKick(time) {
    const ctx = initAudioContext();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.connect(gain);
    gain.connect(ctx.destination);

    osc.frequency.setValueAtTime(150, time);
    osc.frequency.exponentialRampToValueAtTime(40, time + 0.1);

    gain.gain.setValueAtTime(0.8 * volume, time);
    gain.gain.exponentialRampToValueAtTime(0.01, time + 0.3);

    osc.start(time);
    osc.stop(time + 0.3);
}

function playSnare(time) {
    const ctx = initAudioContext();

    // Noise for snare
    const noiseBuffer = ctx.createBuffer(1, ctx.sampleRate * 0.2, ctx.sampleRate);
    const noiseData = noiseBuffer.getChannelData(0);
    for (let i = 0; i < noiseBuffer.length; i++) {
        noiseData[i] = Math.random() * 2 - 1;
    }

    const noise = ctx.createBufferSource();
    noise.buffer = noiseBuffer;

    const noiseFilter = ctx.createBiquadFilter();
    noiseFilter.type = 'highpass';
    noiseFilter.frequency.value = 1000;

    const noiseGain = ctx.createGain();
    noiseGain.gain.setValueAtTime(0.5 * volume, time);
    noiseGain.gain.exponentialRampToValueAtTime(0.01, time + 0.15);

    noise.connect(noiseFilter);
    noiseFilter.connect(noiseGain);
    noiseGain.connect(ctx.destination);

    // Body tone
    const osc = ctx.createOscillator();
    const oscGain = ctx.createGain();
    osc.connect(oscGain);
    oscGain.connect(ctx.destination);

    osc.frequency.value = 200;
    oscGain.gain.setValueAtTime(0.4 * volume, time);
    oscGain.gain.exponentialRampToValueAtTime(0.01, time + 0.05);

    noise.start(time);
    noise.stop(time + 0.2);
    osc.start(time);
    osc.stop(time + 0.05);
}

function playHiHat(time, open = false) {
    const ctx = initAudioContext();

    const noiseBuffer = ctx.createBuffer(1, ctx.sampleRate * (open ? 0.3 : 0.05), ctx.sampleRate);
    const noiseData = noiseBuffer.getChannelData(0);
    for (let i = 0; i < noiseBuffer.length; i++) {
        noiseData[i] = Math.random() * 2 - 1;
    }

    const noise = ctx.createBufferSource();
    noise.buffer = noiseBuffer;

    const filter = ctx.createBiquadFilter();
    filter.type = 'highpass';
    filter.frequency.value = 7000;

    const gain = ctx.createGain();
    const duration = open ? 0.3 : 0.05;
    gain.gain.setValueAtTime(0.25 * volume, time);
    gain.gain.exponentialRampToValueAtTime(0.01, time + duration);

    noise.connect(filter);
    filter.connect(gain);
    gain.connect(ctx.destination);

    noise.start(time);
    noise.stop(time + duration);
}

function playRideCymbal(time) {
    const ctx = initAudioContext();

    const osc = ctx.createOscillator();
    const osc2 = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.type = 'triangle';
    osc2.type = 'triangle';
    osc.frequency.value = 350;
    osc2.frequency.value = 620;

    osc.connect(gain);
    osc2.connect(gain);
    gain.connect(ctx.destination);

    gain.gain.setValueAtTime(0.15 * volume, time);
    gain.gain.exponentialRampToValueAtTime(0.01, time + 0.5);

    osc.start(time);
    osc2.start(time);
    osc.stop(time + 0.5);
    osc2.stop(time + 0.5);
}

// Drum patterns
const drumPatterns = {
    basic_rock: {
        name: 'Basic Rock',
        kick: [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
        snare: [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        hihat: [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
        open: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    funk: {
        name: 'Funk',
        kick: [1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0],
        snare: [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0],
        hihat: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        open: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
    },
    blues_shuffle: {
        name: 'Blues Shuffle',
        kick: [1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0],
        snare: [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        hihat: [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
        open: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        swing: true
    },
    jazz_swing: {
        name: 'Jazz Swing',
        kick: [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        snare: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        hihat: [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        ride: [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
        swing: true
    },
    latin: {
        name: 'Latin',
        kick: [1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0],
        snare: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        hihat: [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
        open: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    reggae: {
        name: 'Reggae',
        kick: [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        snare: [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
        hihat: [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0],
        open: [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    disco: {
        name: 'Disco',
        kick: [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
        snare: [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        hihat: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        open: [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1]
    },
    metal: {
        name: 'Metal',
        kick: [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
        snare: [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        hihat: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        open: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    }
};

function getSelectedPattern() {
    const patternSelect = document.getElementById('drumPatternSelect');
    const patternId = patternSelect ? patternSelect.value : 'basic_rock';
    return drumPatterns[patternId] || drumPatterns.basic_rock;
}

function playDrumBeat() {
    const ctx = initAudioContext();
    const slider = document.getElementById('tempoSlider');
    const bpm = slider ? parseInt(slider.value) : 80;
    const pattern = getSelectedPattern();

    // Time for one 16th note
    const sixteenthTime = (60 / bpm) / 4;
    const swingAmount = pattern.swing ? 0.33 : 0;

    const step = currentBeat % 16;
    const time = ctx.currentTime;

    // Apply swing to off-beat 16th notes
    let offset = 0;
    if (swingAmount > 0 && step % 2 === 1) {
        offset = sixteenthTime * swingAmount;
    }

    // Play drum sounds based on pattern
    if (pattern.kick[step]) playKick(time + offset);
    if (pattern.snare[step]) playSnare(time + offset);
    if (pattern.open && pattern.open[step]) {
        playHiHat(time + offset, true);
    } else if (pattern.hihat[step]) {
        playHiHat(time + offset, false);
    }
    if (pattern.ride && pattern.ride[step]) playRideCymbal(time + offset);

    currentBeat++;
}

function toggleTiming() {
    const btn = document.getElementById('metronomeBtn');
    if (!btn) return;

    if (timingRunning) {
        if (timingInterval) {
            clearInterval(timingInterval);
            timingInterval = null;
        }
        timingRunning = false;
        currentBeat = 0;
        btn.innerHTML = '<i class="bi bi-play-fill"></i> Start';
    } else {
        initAudioContext();
        const slider = document.getElementById('tempoSlider');
        const bpm = slider ? parseInt(slider.value) : 80;

        timingRunning = true;
        btn.innerHTML = '<i class="bi bi-stop-fill"></i> Stop';

        if (isDrumMode()) {
            const sixteenthTime = (60000 / bpm) / 4;
            currentBeat = 0;
            playDrumBeat();
            timingInterval = setInterval(playDrumBeat, sixteenthTime);
        } else {
            const intervalMs = 60000 / bpm;
            let beatCount = 0;
            const playMetronomeClick = () => {
                playClick(beatCount % 4 === 0);
                beatCount++;
            };
            playMetronomeClick();
            timingInterval = setInterval(playMetronomeClick, intervalMs);
        }
    }
}

function adjustTempo(delta) {
    const slider = document.getElementById('tempoSlider');
    if (!slider) return;

    let newValue = parseInt(slider.value) + delta;
    newValue = Math.max(40, Math.min(200, newValue));
    slider.value = newValue;
    const display = document.getElementById('bpmDisplay');
    if (display) display.textContent = newValue;

    if (timingRunning) {
        toggleTiming();
        toggleTiming();
    }
}

function markExerciseComplete() {
    const btn = document.getElementById('completeExerciseBtn');
    const status = document.getElementById('completeStatus');
    if (!btn || !status) return;

    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Saving...';

    fetch('/exercises/complete', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            category: window.exerciseCategory,
            duration: window.exerciseEstimatedDuration
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                btn.innerHTML = '<i class="bi bi-check-circle"></i> Completed!';
                btn.classList.remove('btn-success');
                btn.classList.add('btn-secondary');
                status.innerHTML = `
                    <div class="alert alert-success mb-0">
                        <i class="bi bi-check-circle"></i> 
                        Progress updated! Skill level: ${(data.skill_level * 100).toFixed(1)}% 
                        (${data.exercises_completed} exercises completed)
                    </div>
                `;
            } else {
                btn.disabled = false;
                btn.innerHTML = '<i class="bi bi-check-circle"></i> Mark as Complete';
                status.innerHTML = '<div class="alert alert-danger mb-0">Error updating progress</div>';
            }
        })
        .catch(error => {
            btn.disabled = false;
            btn.innerHTML = '<i class="bi bi-check-circle"></i> Mark as Complete';
            status.innerHTML = '<div class="alert alert-danger mb-0">Error updating progress</div>';
        });
}

// Global scope for onclick attributes
window.startTimer = startTimer;
window.pauseTimer = pauseTimer;
window.resetTimer = resetTimer;
window.toggleTiming = toggleTiming;
window.adjustTempo = adjustTempo;
window.markExerciseComplete = markExerciseComplete;

// Event Listeners
const modeMetronome = document.getElementById('modeMetronome');
if (modeMetronome) {
    modeMetronome.addEventListener('change', function () {
        const section = document.getElementById('drumPatternSection');
        if (section) section.style.display = 'none';
        if (timingRunning) {
            toggleTiming();
            toggleTiming();
        }
    });
}

const modeDrums = document.getElementById('modeDrums');
if (modeDrums) {
    modeDrums.addEventListener('change', function () {
        const section = document.getElementById('drumPatternSection');
        if (section) section.style.display = 'block';
        if (timingRunning) {
            toggleTiming();
            toggleTiming();
        }
    });
}

const tempoSlider = document.getElementById('tempoSlider');
if (tempoSlider) {
    tempoSlider.addEventListener('input', function () {
        const display = document.getElementById('bpmDisplay');
        if (display) display.textContent = this.value;
    });

    tempoSlider.addEventListener('change', function () {
        if (timingRunning) {
            toggleTiming();
            toggleTiming();
        }
    });
}

const drumPatternSelect = document.getElementById('drumPatternSelect');
if (drumPatternSelect) {
    drumPatternSelect.addEventListener('change', function () {
        currentBeat = 0;
        if (timingRunning && isDrumMode()) {
            toggleTiming();
            toggleTiming();
        }
    });
}

const volumeSlider = document.getElementById('volumeSlider');
if (volumeSlider) {
    volumeSlider.addEventListener('input', function () {
        volume = this.value / 100;
    });
}
