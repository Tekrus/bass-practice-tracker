// =============================================================================
// Scoring Constants (mirror Python backend)
// =============================================================================
const SCORE_PERFECT = 100;
const SCORE_GOOD = 50;
const SCORE_OK = 25;
const SCORE_EARLY = 10;
const SCORE_LATE = 10;
const SCORE_MISS = 0;

const STREAK_MULTIPLIERS = {
    5: 1.5,
    10: 2.0,
    20: 2.5,
    50: 3.0,
    100: 4.0
};

// =============================================================================
// Audio Input Handler
// =============================================================================
class AudioInputHandler {
    constructor() {
        this.audioContext = null;
        this.analyser = null;
        this.mediaStream = null;
        this.isConnected = false;
        this.threshold = 30;
        this.noiseFloor = 0;
        this.onNoteDetected = null;
        this.lastTriggerTime = 0;
        this.minTriggerInterval = 200;  // Minimum time between notes
        this.isTriggered = false;  // Gate state - true when above threshold
        this.releaseThreshold = 0;  // Will be set to threshold * 0.5
    }

    async connect(deviceId = null) {
        try {
            const constraints = {
                audio: deviceId ? { deviceId: { exact: deviceId } } : true
            };

            this.mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();

            this.analyser = this.audioContext.createAnalyser();
            this.analyser.fftSize = 512;
            this.analyser.smoothingTimeConstant = 0.2;

            const source = this.audioContext.createMediaStreamSource(this.mediaStream);
            source.connect(this.analyser);

            this.isConnected = true;
            this.startListening();

            return true;
        } catch (error) {
            console.error('Error connecting audio:', error);
            return false;
        }
    }

    disconnect() {
        if (this.mediaStream) {
            this.mediaStream.getTracks().forEach(track => track.stop());
        }
        if (this.audioContext) {
            this.audioContext.close();
        }
        this.isConnected = false;
    }

    getCurrentVolume() {
        if (!this.analyser) return 0;

        const bufferLength = this.analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        this.analyser.getByteFrequencyData(dataArray);

        // Focus on bass frequencies (lower 5%)
        let sum = 0;
        const bassRange = Math.floor(bufferLength * 0.05);
        for (let i = 0; i < bassRange; i++) {
            sum += dataArray[i];
        }
        return (sum / bassRange / 255) * 100;
    }

    async calibrateThreshold(onProgress = null) {
        return new Promise((resolve) => {
            const samples = [];
            const sampleDuration = 1500;
            const startTime = this.audioContext.currentTime * 1000;

            const sample = () => {
                if (!this.isConnected) {
                    resolve(false);
                    return;
                }

                const volume = this.getCurrentVolume();
                samples.push(volume);

                const elapsed = this.audioContext.currentTime * 1000 - startTime;
                if (onProgress) {
                    onProgress(Math.min(100, (elapsed / sampleDuration) * 100));
                }

                if (elapsed < sampleDuration) {
                    requestAnimationFrame(sample);
                } else {
                    // 95th percentile as noise floor
                    samples.sort((a, b) => a - b);
                    const p95Index = Math.floor(samples.length * 0.95);
                    this.noiseFloor = samples[p95Index];

                    // Threshold with margin above noise (adaptive)
                    this.threshold = Math.min(80, Math.max(15, this.noiseFloor + 12));
                    this.releaseThreshold = this.threshold * 0.5;  // 50% of threshold for release
                    resolve(true);
                }
            };

            sample();
        });
    }

    updateThresholdAdaptive(currentVolume) {
        const decayFactor = 0.98;
        const attackFactor = 0.1;
        if (currentVolume > this.threshold) {
            this.threshold = this.threshold * (1 - attackFactor) + currentVolume * attackFactor;
        } else {
            this.threshold = this.threshold * decayFactor + this.noiseFloor * (1 - decayFactor);
        }
    }

    startListening() {
        if (!this.isConnected) return;

        this.releaseThreshold = this.threshold * 0.5;

        const checkLevel = () => {
            if (!this.isConnected) return;

            const volume = this.getCurrentVolume();

            // Update volume meter
            const meterFill = document.getElementById('volume-meter-fill');
            if (meterFill) {
                meterFill.style.width = Math.min(100, volume * 2) + '%';
            }

            // Update indicator
            const indicator = document.getElementById('audio-status');
            if (indicator) {
                indicator.classList.toggle('active', volume > this.threshold);
            }

            // Gate-based trigger detection
            const now = this.audioContext.currentTime * 1000;

            if (volume > this.threshold && !this.isTriggered) {
                // Signal rose above threshold - trigger!
                if ((now - this.lastTriggerTime) > this.minTriggerInterval) {
                    this.isTriggered = true;
                    this.lastTriggerTime = now;
                    if (this.onNoteDetected) {
                        this.onNoteDetected(now);
                    }
                }
            } else if (volume < this.releaseThreshold && this.isTriggered) {
                // Signal dropped below release threshold - reset gate
                this.isTriggered = false;
            }

            requestAnimationFrame(checkLevel);
        };

        checkLevel();
    }

    static async getDevices() {
        try {
            const devices = await navigator.mediaDevices.enumerateDevices();
            return devices.filter(d => d.kind === 'audioinput');
        } catch (error) {
            return [];
        }
    }
}

// =============================================================================
// Metronome with Lookahead Scheduling
// =============================================================================
class Metronome {
    constructor() {
        this.audioContext = null;
        this.nextNoteTime = 0;
        this.lookahead = 25;
        this.scheduleAheadTime = 0.1;
        this.timerID = null;
        this.isRunning = false;
        this.currentBeat = 0;
        this.onBeat = null;
    }

    init() {
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }

    start(tempo, onBeat = null) {
        if (this.isRunning) this.stop();

        if (this.audioContext.state === 'suspended') {
            this.audioContext.resume();
        }

        this.onBeat = onBeat;
        this.currentBeat = 0;
        this.nextNoteTime = this.audioContext.currentTime;
        this.isRunning = true;
        this.scheduler();
    }

    stop() {
        this.isRunning = false;
        if (this.timerID) {
            clearTimeout(this.timerID);
            this.timerID = null;
        }
    }

    getCurrentTime() {
        return this.audioContext ? this.audioContext.currentTime * 1000 : 0;
    }

    scheduler() {
        if (!this.isRunning) return;

        while (this.nextNoteTime < this.audioContext.currentTime + this.scheduleAheadTime) {
            this.scheduleNote(this.nextNoteTime, this.currentBeat);
            this.nextNoteTime += 60 / this.tempo;
            this.currentBeat++;
        }

        this.timerID = setTimeout(() => this.scheduler(), this.lookahead);
    }

    setTempo(tempo) {
        this.tempo = tempo;
    }

    scheduleNote(time, beat) {
        const osc = this.audioContext.createOscillator();
        const gain = this.audioContext.createGain();

        osc.connect(gain);
        gain.connect(this.audioContext.destination);

        const isAccent = beat % 4 === 0;
        osc.frequency.value = isAccent ? 1000 : 800;
        gain.gain.value = isAccent ? 0.3 : 0.2;

        osc.start(time);
        gain.gain.exponentialRampToValueAtTime(0.001, time + 0.05);
        osc.stop(time + 0.05);

        if (this.onBeat) {
            const delay = (time - this.audioContext.currentTime) * 1000;
            if (delay > 0) {
                setTimeout(() => this.onBeat(beat), Math.min(delay, 50));
            }
        }
    }

    playClick(time, isAccent = false) {
        const osc = this.audioContext.createOscillator();
        const gain = this.audioContext.createGain();

        osc.connect(gain);
        gain.connect(this.audioContext.destination);

        osc.frequency.value = isAccent ? 1000 : 800;
        gain.gain.value = isAccent ? 0.3 : 0.2;

        osc.start(time);
        gain.gain.exponentialRampToValueAtTime(0.001, time + 0.05);
        osc.stop(time + 0.05);
    }
}

// =============================================================================
// Calibration Controller
// =============================================================================
class CalibrationController {
    constructor(audioHandler, metronome) {
        this.audioHandler = audioHandler;
        this.metronome = metronome;

        // Calibration state
        this.isCalibrating = false;
        this.currentStep = null;

        // Threshold calibration
        this.signalConfirmCount = 0;
        this.requiredConfirms = 3;

        // Results
        this.systemLatency = 50;  // Default latency estimate (ms)
        this.calibrationOffset = 0;

        this.loadCalibration();
    }

    loadCalibration() {
        try {
            const savedLatency = localStorage.getItem('timing_system_latency');
            const savedThreshold = localStorage.getItem('timing_threshold');

            if (savedLatency !== null) {
                this.systemLatency = parseFloat(savedLatency);
            }
            if (savedThreshold !== null) {
                this.audioHandler.threshold = parseFloat(savedThreshold);
                this.audioHandler.releaseThreshold = this.audioHandler.threshold * 0.5;
            }
            this.updateOffsetDisplay();
        } catch (e) {
            console.error('Error loading calibration:', e);
        }
    }

    saveCalibration() {
        try {
            localStorage.setItem('timing_system_latency', this.systemLatency.toString());
            localStorage.setItem('timing_threshold', this.audioHandler.threshold.toString());
            this.calibrationOffset = this.systemLatency;
            this.audioHandler.releaseThreshold = this.audioHandler.threshold * 0.5;
            this.updateOffsetDisplay();
        } catch (e) {
            console.error('Error saving calibration:', e);
        }
    }

    updateOffsetDisplay() {
        const display = document.getElementById('calibration-offset-display');
        if (display) {
            display.textContent = `${this.systemLatency}ms`;
            display.className = 'badge bg-success';
        }

        const thresholdDisplay = document.getElementById('threshold-value');
        if (thresholdDisplay) {
            thresholdDisplay.textContent = Math.round(this.audioHandler.threshold);
        }
    }

    getOffset() {
        return this.calibrationOffset;
    }

    // Start calibration flow
    start() {
        this.isCalibrating = true;
        this.currentStep = null;
        this.reset();
        this.startThresholdCalibration();
    }

    reset() {
        if (this.isCalibrating === false && this.currentStep === 'results') {
            return;
        }
        document.getElementById('calibration-step-threshold').style.display = 'block';
        document.getElementById('threshold-ambient').style.display = 'block';
        document.getElementById('threshold-confirm').style.display = 'none';
        document.getElementById('ambient-progress').style.width = '0%';

        for (let i = 0; i < 3; i++) {
            const dot = document.getElementById(`thresh-dot-${i}`);
            if (dot) {
                dot.classList.remove('complete', 'current');
            }
        }
    }

    // Step 1a: Sample ambient noise
    async startThresholdCalibration() {
        this.currentStep = 'threshold-ambient';
        const progressBar = document.getElementById('ambient-progress');

        const success = await this.audioHandler.calibrateThreshold((progress) => {
            progressBar.style.width = progress + '%';
        });

        if (success && this.isCalibrating) {
            document.getElementById('threshold-ambient').style.display = 'none';
            document.getElementById('threshold-confirm').style.display = 'block';
            this.startSignalConfirmation();
        }
    }

    // Step 1b: Confirm signal detection
    startSignalConfirmation() {
        this.currentStep = 'threshold-confirm';
        this.signalConfirmCount = 0;

        const indicator = document.getElementById('threshold-indicator');
        const status = document.getElementById('threshold-status');

        document.getElementById('thresh-dot-0').classList.add('current');

        this.audioHandler.onNoteDetected = () => {
            if (!this.isCalibrating || this.currentStep !== 'threshold-confirm') return;

            indicator.classList.add('active');
            setTimeout(() => indicator.classList.remove('active'), 200);

            const currentDot = document.getElementById(`thresh-dot-${this.signalConfirmCount}`);
            if (currentDot) {
                currentDot.classList.remove('current');
                currentDot.classList.add('complete');
            }

            this.signalConfirmCount++;

            const nextDot = document.getElementById(`thresh-dot-${this.signalConfirmCount}`);
            if (nextDot) nextDot.classList.add('current');

            if (this.signalConfirmCount >= this.requiredConfirms) {
                this.audioHandler.onNoteDetected = null;
                this.completeCalibration();
            } else {
                status.textContent = `Detected ${this.signalConfirmCount}/${this.requiredConfirms}...`;
            }
        };

        status.textContent = 'Play some notes...';
    }

    completeCalibration() {
        this.currentStep = 'results';
        this.isCalibrating = false;
        this.audioHandler.onNoteDetected = null;

        document.getElementById('calibration-step-threshold').style.display = 'none';
        document.getElementById('calibration-step-results').style.display = 'block';

        document.getElementById('result-latency').textContent = `${this.systemLatency}ms (estimated)`;
        document.getElementById('result-threshold').textContent = Math.round(this.audioHandler.threshold);
    }

    apply() {
        this.saveCalibration();
    }

    cancel() {
        this.isCalibrating = false;
        this.currentStep = null;
        this.audioHandler.onNoteDetected = null;
    }
}

// =============================================================================
// Game Controller
// =============================================================================
class TimingGame {
    constructor() {
        this.audioHandler = new AudioInputHandler();
        this.metronome = new Metronome();
        this.calibration = null;

        // Game state
        this.sessionId = null;
        this.gameMode = 'groove';
        this.difficulty = 1;
        this.tempo = 80;
        this.durationBars = 8;
        this.isPlaying = false;

        // Timing data
        this.beatTimes = [];
        this.adjustedBeatTimes = [];
        this.leadTime = 0;
        this.gameStartTime = 0;

        // Scoring windows
        this.perfectWindow = 80;
        this.goodWindow = 150;
        this.detectionWindow = 375;

        // Score tracking
        this.score = 0;
        this.streak = 0;
        this.bestStreak = 0;
        this.notesHit = 0;
        this.hits = [];

        // DOM elements
        this.noteElements = [];

        // Calibration
        this.calibrationOffset = 0;
    }

    async init() {
        this.metronome.init();
        this.calibration = new CalibrationController(this.audioHandler, this.metronome);
        this.calibrationOffset = this.calibration.getOffset();
        this.calibration.updateOffsetDisplay();
        this.setupEventListeners();
        await this.loadAudioDevices();
    }

    async loadAudioDevices() {
        const devices = await AudioInputHandler.getDevices();
        const select = document.getElementById('audio-device-select');
        select.innerHTML = '';

        if (devices.length === 0) {
            select.innerHTML = '<option value="">No audio devices found</option>';
            return;
        }

        devices.forEach(device => {
            const option = document.createElement('option');
            option.value = device.deviceId;
            option.textContent = device.label || `Audio Input ${select.children.length + 1}`;
            select.appendChild(option);
        });
    }

    setupEventListeners() {
        // Connect audio
        document.getElementById('connect-audio-btn').addEventListener('click', async () => {
            const setupPanel = document.getElementById('audio-setup-panel');
            if (!this.audioHandler.isConnected) {
                setupPanel.style.display = 'block';
                const deviceId = document.getElementById('audio-device-select').value;
                const success = await this.audioHandler.connect(deviceId || null);

                if (success) {
                    document.getElementById('audio-status').classList.add('connected');
                    document.getElementById('audio-status-text').textContent = 'Connected';
                    document.getElementById('connect-audio-btn').innerHTML = '<i class="bi bi-mic-mute"></i> Disconnect';
                    document.getElementById('start-game-btn').disabled = false;
                }
            } else {
                this.audioHandler.disconnect();
                document.getElementById('audio-status').classList.remove('connected');
                document.getElementById('audio-status-text').textContent = 'Not connected';
                document.getElementById('connect-audio-btn').innerHTML = '<i class="bi bi-mic"></i> Connect Audio';
                document.getElementById('start-game-btn').disabled = true;
                setupPanel.style.display = 'none';
            }
        });

        // Device select
        document.getElementById('audio-device-select').addEventListener('change', async (e) => {
            if (this.audioHandler.isConnected) {
                this.audioHandler.disconnect();
                await this.audioHandler.connect(e.target.value);
            }
        });

        // Calibration
        document.getElementById('calibrate-btn').addEventListener('click', () => {
            if (!this.audioHandler.isConnected) {
                alert('Please connect audio first!');
                return;
            }
            new bootstrap.Modal(document.getElementById('calibration-modal')).show();
            setTimeout(() => this.calibration.start(), 300);
        });

        document.getElementById('recalibrate-btn').addEventListener('click', () => {
            this.calibration.start();
        });

        document.getElementById('apply-calibration-btn').addEventListener('click', () => {
            this.calibration.apply();
            this.calibrationOffset = this.calibration.getOffset();
            bootstrap.Modal.getInstance(document.getElementById('calibration-modal')).hide();
        });

        document.getElementById('calibration-modal').addEventListener('hidden.bs.modal', () => {
            if (this.calibration.isCalibrating) {
                this.calibration.cancel();
            }
        });

        // Game mode selection
        document.querySelectorAll('.game-card').forEach(card => {
            card.addEventListener('click', () => {
                document.querySelectorAll('.game-card').forEach(c => c.classList.remove('selected'));
                card.classList.add('selected');
                this.gameMode = card.dataset.mode;
            });
        });

        // Difficulty selection
        document.querySelectorAll('.difficulty-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.difficulty-btn').forEach(b => b.classList.remove('selected'));
                btn.classList.add('selected');
                this.difficulty = parseInt(btn.dataset.difficulty);
            });
        });

        // Random tempo
        document.getElementById('random-tempo-btn').addEventListener('click', () => {
            document.getElementById('tempo-input').value = Math.floor(Math.random() * 80) + 60;
        });

        // Start/Stop game
        document.getElementById('start-game-btn').addEventListener('click', () => this.startGame());
        document.getElementById('stop-game-btn').addEventListener('click', () => this.stopGame());

        // Play again
        document.getElementById('play-again-btn').addEventListener('click', () => {
            bootstrap.Modal.getInstance(document.getElementById('results-modal')).hide();
            this.startGame();
        });

        // Results modal close
        document.getElementById('results-modal').addEventListener('hidden.bs.modal', () => {
            document.getElementById('game-selection').style.display = 'block';
            document.getElementById('game-container').style.display = 'none';
        });

        // Keyboard fallback
        document.addEventListener('keydown', (e) => {
            if (this.isPlaying && e.code === 'Space') {
                e.preventDefault();
                this.registerHit(this.metronome.getCurrentTime() - this.gameStartTime);
            }
        });
    }

    async startGame() {
        this.tempo = parseInt(document.getElementById('tempo-input').value) || 80;
        this.durationBars = parseInt(document.getElementById('duration-select').value) || 8;

        if (!document.querySelector('.game-card.selected')) {
            alert('Please select a game mode!');
            return;
        }

        try {
            const response = await fetch('/timing/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    game_mode: this.gameMode,
                    difficulty: this.difficulty,
                    tempo: this.tempo,
                    duration_bars: this.durationBars
                })
            });

            const data = await response.json();
            this.sessionId = data.session_id;
            this.beatTimes = data.beat_times;
            this.tempo = data.tempo;

            // Calculate timing windows
            const beatInterval = 60000 / this.tempo;
            this.perfectWindow = data.perfect_window_ms;
            this.goodWindow = data.good_window_ms;
            this.detectionWindow = Math.min(beatInterval / 2, data.good_window_ms * 1.5);

            document.getElementById('total-notes').textContent = data.total_notes;
            document.getElementById('current-tempo').textContent = data.tempo;

            // Audio handler callback
            this.audioHandler.onNoteDetected = (time) => {
                if (this.isPlaying) {
                    this.registerHit(time - this.gameStartTime);
                }
            };

            // Show game UI
            document.getElementById('game-selection').style.display = 'none';
            document.getElementById('game-container').style.display = 'block';

            await this.showCountdown();
            this.startGameLoop();

        } catch (error) {
            console.error('Error starting game:', error);
            alert('Error starting game.');
        }
    }

    async showCountdown() {
        return new Promise(resolve => {
            const countdownScreen = document.getElementById('countdown-screen');
            const gameScreen = document.getElementById('game-screen');
            const countdownNumber = document.getElementById('countdown-number');

            countdownScreen.style.display = 'block';
            gameScreen.style.display = 'none';

            document.getElementById('countdown-tempo').textContent = this.tempo;

            const beatInterval = 60000 / this.tempo;
            let beat = 0;
            const totalBeats = 4;

            // Use audio context time for precise countdown scheduling
            const startTime = this.metronome.audioContext.currentTime;

            const playCountBeat = () => {
                beat++;

                if (beat <= totalBeats) {
                    countdownNumber.textContent = totalBeats - beat + 1;
                    const clickTime = startTime + (beat * beatInterval / 1000);
                    this.metronome.playClick(clickTime, beat === 1);
                    setTimeout(playCountBeat, beatInterval);
                } else {
                    countdownScreen.style.display = 'none';
                    gameScreen.style.display = 'block';
                    resolve();
                }
            };

            playCountBeat();
        });
    }

    startGameLoop() {
        this.isPlaying = true;
        this.score = 0;
        this.streak = 0;
        this.bestStreak = 0;
        this.notesHit = 0;
        this.hits = [];

        // Lead time: 2 beats
        const beatDuration = 60000 / this.tempo;
        this.leadTime = beatDuration * 2;
        this.adjustedBeatTimes = this.beatTimes.map(t => t + this.leadTime);

        // Use audio context time for precise game timing
        this.gameStartTime = this.metronome.getCurrentTime();

        this.createNotes();

        // Start metronome with lookahead scheduling
        this.metronome.setTempo(this.tempo);
        this.metronome.start(this.tempo);

        this.animationLoop();
    }

    // Get precise current time using audio context
    getCurrentGameTime() {
        return this.metronome.getCurrentTime() - this.gameStartTime;
    }

    animationLoop() {
        if (!this.isPlaying) return;

        const currentTime = this.getCurrentGameTime();
        const beatTimes = this.adjustedBeatTimes;
        const totalDuration = beatTimes[beatTimes.length - 1] + 1000;

        // Progress
        document.getElementById('game-progress').style.width = Math.min(100, (currentTime / totalDuration) * 100) + '%';

        // Time remaining
        const remaining = Math.max(0, totalDuration - currentTime) / 1000;
        document.getElementById('time-remaining').textContent =
            `${Math.floor(remaining / 60)}:${Math.floor(remaining % 60).toString().padStart(2, '0')}`;

        // Animate notes
        const approachTime = 2000;
        const MISS_GRACE_PERIOD = 100;

        this.noteElements.forEach((note, index) => {
            const noteTime = beatTimes[index];
            const timeUntilNote = noteTime - currentTime;

            // Position
            if (timeUntilNote > approachTime) {
                note.style.display = 'none';
            } else if (timeUntilNote > -this.detectionWindow - 200) {
                note.style.display = 'flex';
                note.style.left = (50 + (timeUntilNote / approachTime) * 50) + '%';
            } else {
                note.style.display = 'none';
            }

            // Miss detection with grace period
            if (timeUntilNote < -this.detectionWindow && !this.isNoteProcessed(note)) {
                if (!note.dataset.pendingMissAt) {
                    note.dataset.pendingMissAt = this.metronome.getCurrentTime().toString();
                }

                const pendingTime = parseFloat(note.dataset.pendingMissAt);
                if (this.metronome.getCurrentTime() - pendingTime > MISS_GRACE_PERIOD && !this.isNoteProcessed(note)) {
                    note.classList.add('missed');
                    this.registerMiss(index);
                }
            }
        });

        // Game complete check
        if (currentTime >= totalDuration) {
            this.endGame();
            return;
        }

        requestAnimationFrame(() => this.animationLoop());
    }

    createNotes() {
        const beatTrack = document.getElementById('beat-track');
        beatTrack.querySelectorAll('.beat-note').forEach(n => n.remove());

        this.noteElements = [];

        this.beatTimes.forEach((time, index) => {
            const note = document.createElement('div');
            note.className = 'beat-note';
            note.textContent = index + 1;
            note.style.left = '100%';
            note.dataset.index = index;
            beatTrack.appendChild(note);
            this.noteElements.push(note);
        });
    }

    stopGame() {
        this.isPlaying = false;
        this.metronome.stop();
    }

    // CLIENT-SIDE hit quality calculation
    calculateHitQuality(offsetMs) {
        const absOffset = Math.abs(offsetMs);
        const isEarly = offsetMs < 0;

        if (absOffset <= this.perfectWindow) {
            return { quality: 'perfect', score: SCORE_PERFECT, isEarly };
        } else if (absOffset <= this.goodWindow) {
            return { quality: 'good', score: SCORE_GOOD, isEarly };
        } else if (absOffset <= this.detectionWindow) {
            return { quality: 'ok', score: SCORE_OK, isEarly };
        } else if (isEarly) {
            return { quality: 'early', score: SCORE_EARLY, isEarly: true };
        } else {
            return { quality: 'late', score: SCORE_LATE, isEarly: false };
        }
    }

    getStreakMultiplier() {
        let multiplier = 1.0;
        for (const [threshold, mult] of Object.entries(STREAK_MULTIPLIERS)) {
            if (this.streak >= parseInt(threshold)) {
                multiplier = mult;
            }
        }
        return multiplier;
    }

    getFirstUnhitNoteIndex() {
        for (let i = 0; i < this.noteElements.length; i++) {
            if (!this.isNoteProcessed(this.noteElements[i])) {
                return i;
            }
        }
        return -1;
    }

    isNoteProcessed(note) {
        return note.classList.contains('hit-perfect') ||
            note.classList.contains('hit-good') ||
            note.classList.contains('hit-ok') ||
            note.classList.contains('hit-early') ||
            note.classList.contains('hit-late') ||
            note.classList.contains('missed');
    }

    getRelaxedFirstNoteWindow() {
        return 60000 / this.tempo; // 1 beat
    }

    // CLIENT-SIDE hit registration (no network call!)
    registerHit(hitTime) {
        const calibratedHitTime = hitTime - this.calibrationOffset;
        const beatTimes = this.adjustedBeatTimes;

        const firstUnhitIndex = this.getFirstUnhitNoteIndex();
        let closestIndex = -1;
        let closestOffset = Infinity;

        for (let i = 0; i < beatTimes.length; i++) {
            const note = this.noteElements[i];
            if (this.isNoteProcessed(note)) continue;

            const offset = calibratedHitTime - beatTimes[i];
            const absOffset = Math.abs(offset);

            // Relaxed window for first note
            const earlyBound = (i === firstUnhitIndex) ? this.getRelaxedFirstNoteWindow() : this.detectionWindow;
            const lateBound = this.detectionWindow;

            if (offset >= -earlyBound && offset <= lateBound) {
                if (absOffset < Math.abs(closestOffset)) {
                    closestOffset = offset;
                    closestIndex = i;
                }
            }
        }

        if (closestIndex === -1) return;

        // Calculate quality CLIENT-SIDE
        const { quality, score, isEarly } = this.calculateHitQuality(closestOffset);

        // Update streak
        if (quality === 'perfect' || quality === 'good' || quality === 'ok') {
            this.streak++;
            this.bestStreak = Math.max(this.bestStreak, this.streak);
        } else {
            this.streak = 0;
        }

        // Apply multiplier
        const finalScore = Math.floor(score * this.getStreakMultiplier());

        // Store hit
        this.hits.push({
            note_index: closestIndex,
            offset_ms: closestOffset,
            quality: quality,
            score: finalScore
        });

        // Update visuals IMMEDIATELY
        const note = this.noteElements[closestIndex];
        note.classList.add('hit-' + quality);

        this.score += finalScore;
        this.notesHit++;

        document.getElementById('current-score').textContent = this.score;
        document.getElementById('current-streak').textContent = this.streak;
        document.getElementById('notes-hit').textContent = this.notesHit;

        const feedback = document.getElementById('hit-feedback');
        feedback.className = 'hit-feedback ' + quality;
        feedback.textContent = quality.toUpperCase();

        document.getElementById('timing-offset').textContent = isEarly ?
            `${Math.abs(closestOffset).toFixed(0)}ms early` :
            closestOffset > 0 ? `${closestOffset.toFixed(0)}ms late` : 'Perfect!';

        document.getElementById('streak-display').classList.toggle('on-fire', this.streak >= 5);
    }

    // CLIENT-SIDE miss registration (no network call!)
    registerMiss(noteIndex) {
        this.hits.push({
            note_index: noteIndex,
            offset_ms: null,
            quality: 'miss',
            score: 0
        });

        this.streak = 0;
        document.getElementById('current-streak').textContent = '0';
        document.getElementById('streak-display').classList.remove('on-fire');

        const feedback = document.getElementById('hit-feedback');
        feedback.className = 'hit-feedback miss';
        feedback.textContent = 'MISS';
        document.getElementById('timing-offset').textContent = '';
    }

    // Send all hits at game end (single network call)
    async endGame() {
        this.isPlaying = false;
        this.metronome.stop();

        const duration = Math.floor(this.getCurrentGameTime() / 1000);

        try {
            const response = await fetch('/timing/complete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    duration_seconds: duration,
                    hits: this.hits  // All hits sent at once
                })
            });

            const data = await response.json();
            this.showResults(data);

        } catch (error) {
            console.error('Error completing game:', error);
            // Fallback to client-calculated results
            this.showResults({
                stats: this.calculateClientStats(),
                tips: ['Session completed.'],
                is_new_high_score: false
            });
        }
    }

    calculateClientStats() {
        let perfect = 0, good = 0, ok = 0, early = 0, late = 0, miss = 0;
        let totalScore = 0;
        const offsets = [];

        for (const hit of this.hits) {
            totalScore += hit.score;
            if (hit.quality === 'perfect') { perfect++; if (hit.offset_ms !== null) offsets.push(hit.offset_ms); }
            else if (hit.quality === 'good') { good++; if (hit.offset_ms !== null) offsets.push(hit.offset_ms); }
            else if (hit.quality === 'ok') { ok++; if (hit.offset_ms !== null) offsets.push(hit.offset_ms); }
            else if (hit.quality === 'early') { early++; }
            else if (hit.quality === 'late') { late++; }
            else { miss++; }
        }

        const total = this.hits.length;
        const accurate = perfect + good + ok;

        return {
            total_score: totalScore,
            total_notes: total,
            perfect_hits: perfect,
            good_hits: good,
            ok_hits: ok,
            early_hits: early,
            late_hits: late,
            missed_notes: miss,
            best_streak: this.bestStreak,
            accuracy_percentage: total ? Math.round(accurate / total * 1000) / 10 : 0,
            average_timing_ms: offsets.length ? Math.round(offsets.reduce((a, b) => a + b, 0) / offsets.length * 100) / 100 : 0
        };
    }

    showResults(data) {
        const stats = data.stats;

        document.getElementById('result-score').textContent = stats.total_score;
        document.getElementById('result-accuracy').textContent = stats.accuracy_percentage + '%';
        document.getElementById('result-streak').textContent = stats.best_streak;

        document.getElementById('result-perfect').textContent = stats.perfect_hits;
        document.getElementById('result-good').textContent = stats.good_hits;
        document.getElementById('result-ok').textContent = stats.ok_hits || 0;
        document.getElementById('result-early').textContent = stats.early_hits;
        document.getElementById('result-late').textContent = stats.late_hits;
        document.getElementById('result-miss').textContent = stats.missed_notes;

        // Timing breakdown bar
        const total = stats.total_notes;
        const breakdown = document.getElementById('timing-breakdown');
        breakdown.innerHTML = '';

        const segments = [
            { class: 'perfect', count: stats.perfect_hits },
            { class: 'good', count: stats.good_hits },
            { class: 'ok', count: stats.ok_hits || 0 },
            { class: 'early', count: stats.early_hits },
            { class: 'late', count: stats.late_hits },
            { class: 'miss', count: stats.missed_notes },
        ];

        segments.forEach(seg => {
            if (seg.count > 0) {
                const div = document.createElement('div');
                div.className = 'segment ' + seg.class;
                div.style.width = (seg.count / total * 100) + '%';
                div.textContent = seg.count;
                breakdown.appendChild(div);
            }
        });

        // Tips
        const tipsList = document.getElementById('result-tips');
        tipsList.innerHTML = '';
        (data.tips || []).forEach(tip => {
            const li = document.createElement('li');
            li.className = 'mb-2';
            li.innerHTML = '<i class="bi bi-lightbulb text-warning me-2"></i>' + tip;
            tipsList.appendChild(li);
        });

        // High score
        document.getElementById('new-high-score-banner').style.display =
            data.is_new_high_score ? 'block' : 'none';

        new bootstrap.Modal(document.getElementById('results-modal')).show();
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    const game = new TimingGame();
    game.init();
});
