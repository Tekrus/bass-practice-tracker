// Session Timer
let sessionSeconds = 0;
let sessionRunning = false;
let sessionInterval;

const timerToggle = document.getElementById('timerToggle');
if (timerToggle) {
    timerToggle.addEventListener('click', function () {
        sessionRunning = !sessionRunning;
        this.innerHTML = sessionRunning ? '<i class="bi bi-pause-fill"></i>' : '<i class="bi bi-play-fill"></i>';

        if (sessionRunning) {
            sessionInterval = setInterval(updateSessionTimer, 1000);
        } else {
            clearInterval(sessionInterval);
        }
    });
}

function updateSessionTimer() {
    sessionSeconds++;
    const mins = Math.floor(sessionSeconds / 60);
    const secs = sessionSeconds % 60;
    const sessionTimer = document.getElementById('sessionTimer');
    const actualDurationInput = document.getElementById('actualDurationInput');

    if (sessionTimer) {
        sessionTimer.textContent = String(mins).padStart(2, '0') + ':' + String(secs).padStart(2, '0');
    }
    if (actualDurationInput) {
        actualDurationInput.value = Math.ceil(sessionSeconds / 60);
    }
}

// Exercise Timer
let exerciseSeconds = 300;
let exerciseRunning = false;
let exerciseInterval;

function updateExerciseTimerDisplay() {
    const mins = Math.floor(exerciseSeconds / 60);
    const secs = exerciseSeconds % 60;
    const exerciseTimer = document.getElementById('exerciseTimer');
    if (exerciseTimer) {
        exerciseTimer.textContent = String(mins).padStart(2, '0') + ':' + String(secs).padStart(2, '0');
    }
}

function setExerciseTimer(minutes) {
    exerciseSeconds = minutes * 60;
    updateExerciseTimerDisplay();
    if (exerciseRunning) {
        clearInterval(exerciseInterval);
        exerciseRunning = false;
        const startBtn = document.getElementById('exerciseTimerStart');
        if (startBtn) startBtn.innerHTML = '<i class="bi bi-play-fill"></i> Start';
    }
}

const exerciseTimerStart = document.getElementById('exerciseTimerStart');
if (exerciseTimerStart) {
    exerciseTimerStart.addEventListener('click', function () {
        exerciseRunning = !exerciseRunning;
        this.innerHTML = exerciseRunning ? '<i class="bi bi-pause-fill"></i> Pause' : '<i class="bi bi-play-fill"></i> Start';

        if (exerciseRunning) {
            exerciseInterval = setInterval(function () {
                exerciseSeconds--;
                updateExerciseTimerDisplay();
                if (exerciseSeconds <= 0) {
                    clearInterval(exerciseInterval);
                    exerciseRunning = false;
                    const startBtn = document.getElementById('exerciseTimerStart');
                    if (startBtn) startBtn.innerHTML = '<i class="bi bi-play-fill"></i> Start';
                    // Play notification sound
                    new Audio('data:audio/wav;base64,UklGRl9vT19XQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YU').play().catch(() => { });
                    alert('Timer complete!');
                }
            }, 1000);
        } else {
            clearInterval(exerciseInterval);
        }
    });
}

const exerciseTimerReset = document.getElementById('exerciseTimerReset');
if (exerciseTimerReset) {
    exerciseTimerReset.addEventListener('click', function () {
        setExerciseTimer(5);
    });
}

document.querySelectorAll('.set-timer-btn').forEach(btn => {
    btn.addEventListener('click', function () {
        setExerciseTimer(parseInt(this.dataset.minutes));
    });
});

// Metronome
let bpm = 120;
let metronomeRunning = false;
let metronomeInterval;
let beatIndex = 0;
let audioContext;

function playClick(isAccent) {
    if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }

    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);

    oscillator.frequency.value = isAccent ? 1000 : 800;
    gainNode.gain.setValueAtTime(0.5, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);

    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.1);
}

function updateBeatIndicator() {
    const dots = document.querySelectorAll('.beat-dot');
    dots.forEach((dot, i) => {
        dot.classList.remove('bg-primary');
        dot.classList.add('bg-secondary');
    });
    if (dots[beatIndex]) {
        dots[beatIndex].classList.remove('bg-secondary');
        dots[beatIndex].classList.add('bg-primary');
    }
}

const metronomeToggle = document.getElementById('metronomeToggle');
if (metronomeToggle) {
    metronomeToggle.addEventListener('click', function () {
        metronomeRunning = !metronomeRunning;
        const icon = document.getElementById('metronomeIcon');
        if (icon) icon.className = metronomeRunning ? 'bi bi-pause-fill' : 'bi bi-play-fill';

        if (metronomeRunning) {
            const interval = 60000 / bpm;
            metronomeInterval = setInterval(function () {
                playClick(beatIndex === 0);
                updateBeatIndicator();
                beatIndex = (beatIndex + 1) % 4;
            }, interval);
        } else {
            clearInterval(metronomeInterval);
        }
    });
}

function updateBPM(newBPM) {
    bpm = Math.max(40, Math.min(240, newBPM));
    const bpmDisplay = document.getElementById('bpmDisplay');
    const bpmSlider = document.getElementById('bpmSlider');
    if (bpmDisplay) bpmDisplay.textContent = bpm;
    if (bpmSlider) bpmSlider.value = bpm;

    if (metronomeRunning) {
        clearInterval(metronomeInterval);
        const interval = 60000 / bpm;
        if (autoSpeedRunning) {
            startAutoSpeedMetronome();
        } else {
            metronomeInterval = setInterval(function () {
                playClick(beatIndex === 0);
                updateBeatIndicator();
                beatIndex = (beatIndex + 1) % 4;
            }, interval);
        }
    }
}

const bpmSlider = document.getElementById('bpmSlider');
if (bpmSlider) {
    bpmSlider.addEventListener('input', function () {
        updateBPM(parseInt(this.value));
    });
}

const bpmMinus = document.getElementById('bpmMinus');
if (bpmMinus) {
    bpmMinus.addEventListener('click', function () {
        updateBPM(bpm - 5);
    });
}

const bpmPlus = document.getElementById('bpmPlus');
if (bpmPlus) {
    bpmPlus.addEventListener('click', function () {
        updateBPM(bpm + 5);
    });
}

// Auto Speed-Up Metronome
let autoSpeedEnabled = false;
let autoSpeedRunning = false;
let currentBar = 0;
let currentBeat = 0;
let startBpmValue = 80;
let targetBpmValue = 120;
let speedIncrement = 5;
let speedIntervalBars = 4;

const autoSpeedToggle = document.getElementById('autoSpeedToggle');
if (autoSpeedToggle) {
    autoSpeedToggle.addEventListener('change', function () {
        autoSpeedEnabled = this.checked;
        const settings = document.getElementById('autoSpeedSettings');
        if (settings) settings.style.display = this.checked ? 'block' : 'none';

        if (!this.checked && autoSpeedRunning) {
            stopAutoSpeed();
        }
    });
}

const startAutoSpeedBtn = document.getElementById('startAutoSpeed');
if (startAutoSpeedBtn) {
    startAutoSpeedBtn.addEventListener('click', function () {
        if (autoSpeedRunning) {
            stopAutoSpeed();
        } else {
            startAutoSpeedFunc();
        }
    });
}

function startAutoSpeedFunc() {
    // Get values from inputs
    speedIncrement = parseInt(document.getElementById('speedIncrement').value) || 5;
    speedIntervalBars = parseInt(document.getElementById('speedInterval').value) || 4;
    startBpmValue = parseInt(document.getElementById('startBpm').value) || 80;
    targetBpmValue = parseInt(document.getElementById('targetBpm').value) || 120;

    // Validate
    if (startBpmValue >= targetBpmValue) {
        alert('Start BPM must be less than Target BPM');
        return;
    }

    // Reset counters
    currentBar = 0;
    currentBeat = 0;
    beatIndex = 0;

    // Set starting BPM
    updateBPM(startBpmValue);

    // Update UI
    autoSpeedRunning = true;
    const btn = document.getElementById('startAutoSpeed');
    if (btn) {
        btn.innerHTML = '<i class="bi bi-stop-fill"></i> Stop Speed Training';
        btn.classList.remove('btn-outline-success');
        btn.classList.add('btn-danger');
    }
    const progress = document.getElementById('autoSpeedProgress');
    if (progress) progress.style.display = 'block';
    const badge = document.getElementById('autoSpeedBadge');
    if (badge) badge.style.display = 'inline';
    const amount = document.getElementById('autoSpeedAmount');
    if (amount) amount.textContent = speedIncrement;
    const targetDisplay = document.getElementById('targetBpmDisplay');
    if (targetDisplay) targetDisplay.style.display = 'block';
    const targetVal = document.getElementById('targetBpmValue');
    if (targetVal) targetVal.textContent = targetBpmValue;

    // Disable manual BPM controls during auto speed
    const slider = document.getElementById('bpmSlider');
    const minus = document.getElementById('bpmMinus');
    const plus = document.getElementById('bpmPlus');
    const inc = document.getElementById('speedIncrement');
    const interval = document.getElementById('speedInterval');
    const start = document.getElementById('startBpm');
    const target = document.getElementById('targetBpm');

    if (slider) slider.disabled = true;
    if (minus) minus.disabled = true;
    if (plus) plus.disabled = true;
    if (inc) inc.disabled = true;
    if (interval) interval.disabled = true;
    if (start) start.disabled = true;
    if (target) target.disabled = true;

    updateAutoSpeedDisplay();

    // Start metronome if not running
    if (!metronomeRunning) {
        const toggle = document.getElementById('metronomeToggle');
        if (toggle) toggle.click();
    }

    // Override metronome interval with auto-speed tracking
    clearInterval(metronomeInterval);
    startAutoSpeedMetronome();
}

function startAutoSpeedMetronome() {
    const interval = 60000 / bpm;
    metronomeInterval = setInterval(function () {
        playClick(beatIndex === 0);
        updateBeatIndicator();

        // Track beats and bars
        currentBeat++;
        if (currentBeat >= 4) {
            currentBeat = 0;
            currentBar++;

            // Check if we should increase BPM
            if (currentBar % speedIntervalBars === 0 && currentBar > 0) {
                const newBpm = bpm + speedIncrement;

                if (newBpm >= targetBpmValue) {
                    // Reached target!
                    updateBPM(targetBpmValue);
                    flashSpeedIncrease();
                    setTimeout(function () {
                        stopAutoSpeed();
                        showTargetReached();
                    }, 500);
                } else {
                    updateBPM(newBpm);
                    flashSpeedIncrease();
                    // Restart metronome with new BPM
                    clearInterval(metronomeInterval);
                    startAutoSpeedMetronome();
                }
            }

            updateAutoSpeedDisplay();
        }

        beatIndex = (beatIndex + 1) % 4;
    }, interval);
}

function stopAutoSpeed() {
    autoSpeedRunning = false;

    // Update UI
    const btn = document.getElementById('startAutoSpeed');
    if (btn) {
        btn.innerHTML = '<i class="bi bi-lightning"></i> Start Speed Training';
        btn.classList.remove('btn-danger');
        btn.classList.add('btn-outline-success');
    }
    const badge = document.getElementById('autoSpeedBadge');
    if (badge) badge.style.display = 'none';
    const targetDisplay = document.getElementById('targetBpmDisplay');
    if (targetDisplay) targetDisplay.style.display = 'none';

    // Re-enable manual controls
    const slider = document.getElementById('bpmSlider');
    const minus = document.getElementById('bpmMinus');
    const plus = document.getElementById('bpmPlus');
    const inc = document.getElementById('speedIncrement');
    const interval = document.getElementById('speedInterval');
    const start = document.getElementById('startBpm');
    const target = document.getElementById('targetBpm');

    if (slider) slider.disabled = false;
    if (minus) minus.disabled = false;
    if (plus) plus.disabled = false;
    if (inc) inc.disabled = false;
    if (interval) interval.disabled = false;
    if (start) start.disabled = false;
    if (target) target.disabled = false;

    // Stop metronome
    if (metronomeRunning) {
        const toggle = document.getElementById('metronomeToggle');
        if (toggle) toggle.click();
    }
}

function updateAutoSpeedDisplay() {
    const barsUntilNext = speedIntervalBars - (currentBar % speedIntervalBars);
    const cb = document.getElementById('currentBar');
    const bui = document.getElementById('barsUntilIncrease');
    if (cb) cb.textContent = currentBar;
    if (bui) bui.textContent = barsUntilNext;

    // Calculate progress percentage
    const totalBpmRange = targetBpmValue - startBpmValue;
    const currentProgress = bpm - startBpmValue;
    const progressPct = Math.min(100, (currentProgress / totalBpmRange) * 100);
    const progressBar = document.getElementById('speedProgressBar');
    if (progressBar) progressBar.style.width = progressPct + '%';
}

function flashSpeedIncrease() {
    // Visual feedback when speed increases
    const bpmDisplay = document.getElementById('bpmDisplay');
    if (bpmDisplay) {
        bpmDisplay.style.color = '#00ff00';
        bpmDisplay.style.transform = 'scale(1.2)';
        bpmDisplay.style.transition = 'all 0.2s ease';

        setTimeout(function () {
            bpmDisplay.style.color = '';
            bpmDisplay.style.transform = '';
        }, 300);
    }

    // Play a higher pitched "speed up" sound
    if (audioContext) {
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        oscillator.frequency.value = 1200;
        oscillator.type = 'sine';
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.15);

        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.15);
    }
}

function showTargetReached() {
    // Show completion message
    const progressContainer = document.getElementById('autoSpeedProgress');
    if (progressContainer) {
        progressContainer.innerHTML = `
            <div class="alert alert-success py-2 mb-0 mt-2">
                <i class="bi bi-trophy-fill"></i> Target reached! ${targetBpmValue} BPM
            </div>
        `;
    }

    // Play celebration sound
    if (audioContext) {
        const notes = [523.25, 659.25, 783.99, 1046.5]; // C5, E5, G5, C6
        notes.forEach((freq, i) => {
            setTimeout(() => {
                const oscillator = audioContext.createOscillator();
                const gainNode = audioContext.createGain();
                oscillator.connect(gainNode);
                gainNode.connect(audioContext.destination);

                oscillator.frequency.value = freq;
                oscillator.type = 'sine';
                gainNode.gain.setValueAtTime(0.2, audioContext.currentTime);
                gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);

                oscillator.start(audioContext.currentTime);
                oscillator.stop(audioContext.currentTime + 0.3);
            }, i * 150);
        });
    }

    // Reset progress display after a few seconds
    setTimeout(function () {
        const progress = document.getElementById('autoSpeedProgress');
        if (progress) {
            progress.innerHTML = `
                <div class="progress" style="height: 8px;">
                    <div class="progress-bar bg-success" id="speedProgressBar" style="width: 0%"></div>
                </div>
                <small class="text-secondary">
                    Bar <span id="currentBar">0</span> | 
                    Next increase in <span id="barsUntilIncrease">${speedIntervalBars}</span> bars
                </small>
            `;
            progress.style.display = 'none';
        }
    }, 5000);
}

// Complete Exercise Forms
document.querySelectorAll('.complete-exercise-form').forEach(form => {
    form.addEventListener('submit', function (e) {
        e.preventDefault();
        const sessionId = this.dataset.sessionId;
        const exerciseIndex = this.dataset.exerciseIndex;
        const formData = new FormData(this);

        fetch(`/practice/${sessionId}/exercise/${exerciseIndex}/complete`, {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                }
            });
    });
});
