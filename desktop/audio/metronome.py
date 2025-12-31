"""
High-precision metronome with ASIO output support.
"""
import numpy as np
import threading
import time
from typing import Optional, Callable
from .engine import AudioEngine


class Metronome:
    """
    Low-latency metronome with configurable tempo, time signature, and click sounds.
    """
    
    def __init__(self, audio_engine: AudioEngine):
        """
        Initialize metronome with audio engine.
        
        Args:
            audio_engine: AudioEngine instance for audio output
        """
        self.audio = audio_engine
        self.sample_rate = audio_engine.sample_rate
        
        # Metronome settings
        self._tempo = 120  # BPM
        self._beats_per_measure = 4
        self._current_beat = 0
        
        # Click sound parameters
        self._accent_freq = 1000  # Hz for accent (beat 1)
        self._normal_freq = 800   # Hz for normal beats
        self._click_duration = 0.05  # seconds
        
        # Auto speed-up settings
        self._auto_speedup_enabled = False
        self._tempo_increment = 5  # BPM increase
        self._bars_per_increment = 4
        self._max_tempo = 200
        self._bars_played = 0
        
        # Threading
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        
        # Callbacks
        self._beat_callback: Optional[Callable] = None
        self._bar_callback: Optional[Callable] = None
        
        # Pre-generate click sounds
        self._generate_click_sounds()
    
    def _generate_click_sounds(self):
        """Pre-generate click audio samples for low latency."""
        t = np.linspace(0, self._click_duration, 
                        int(self.sample_rate * self._click_duration), False)
        
        # Envelope for smooth click
        envelope = np.exp(-t * 30)
        
        # Accent click (higher pitch)
        self._accent_click = (np.sin(2 * np.pi * self._accent_freq * t) * envelope * 0.8).astype(np.float32)
        
        # Normal click
        self._normal_click = (np.sin(2 * np.pi * self._normal_freq * t) * envelope * 0.6).astype(np.float32)
    
    @property
    def tempo(self) -> int:
        return self._tempo
    
    @tempo.setter
    def tempo(self, bpm: int):
        self._tempo = max(30, min(300, bpm))
    
    @property
    def beats_per_measure(self) -> int:
        return self._beats_per_measure
    
    @beats_per_measure.setter
    def beats_per_measure(self, beats: int):
        self._beats_per_measure = max(1, min(12, beats))
    
    @property
    def is_running(self) -> bool:
        return self._running
    
    def set_beat_callback(self, callback: Optional[Callable]):
        """
        Set callback for each beat.
        Callback signature: callback(beat_number: int, is_accent: bool)
        """
        self._beat_callback = callback
    
    def set_bar_callback(self, callback: Optional[Callable]):
        """
        Set callback for each bar completion.
        Callback signature: callback(bar_number: int, tempo: int)
        """
        self._bar_callback = callback
    
    def enable_auto_speedup(self, 
                            enabled: bool = True,
                            tempo_increment: int = 5,
                            bars_per_increment: int = 4,
                            max_tempo: int = 200):
        """
        Enable/configure automatic tempo increase.
        
        Args:
            enabled: Whether to enable auto speed-up
            tempo_increment: BPM increase per increment
            bars_per_increment: How many bars before increasing tempo
            max_tempo: Maximum tempo to reach
        """
        self._auto_speedup_enabled = enabled
        self._tempo_increment = tempo_increment
        self._bars_per_increment = bars_per_increment
        self._max_tempo = max_tempo
    
    def _metronome_thread(self):
        """Main metronome thread - high precision timing."""
        beat_interval = 60.0 / self._tempo
        next_beat_time = time.perf_counter()
        
        while self._running:
            current_time = time.perf_counter()
            
            if current_time >= next_beat_time:
                # Determine if this is an accent beat
                is_accent = self._current_beat == 0
                
                # Play click
                click = self._accent_click if is_accent else self._normal_click
                self.audio.play_audio(click)
                
                # Call beat callback
                if self._beat_callback:
                    try:
                        self._beat_callback(self._current_beat, is_accent)
                    except Exception as e:
                        print(f"Beat callback error: {e}")
                
                # Update beat counter
                self._current_beat = (self._current_beat + 1) % self._beats_per_measure
                
                # Handle bar completion
                if self._current_beat == 0:
                    self._bars_played += 1
                    
                    # Call bar callback
                    if self._bar_callback:
                        try:
                            self._bar_callback(self._bars_played, self._tempo)
                        except Exception as e:
                            print(f"Bar callback error: {e}")
                    
                    # Auto speed-up
                    if self._auto_speedup_enabled:
                        if self._bars_played % self._bars_per_increment == 0:
                            if self._tempo < self._max_tempo:
                                self._tempo = min(self._tempo + self._tempo_increment, self._max_tempo)
                                # Recalculate beat interval with new tempo
                                beat_interval = 60.0 / self._tempo
                
                # Schedule next beat
                next_beat_time += beat_interval
                
                # Handle drift - if we're too far behind, reset timing
                if current_time > next_beat_time + beat_interval:
                    next_beat_time = current_time + beat_interval
            else:
                # Sleep for a short time to avoid busy-waiting
                sleep_time = min(0.001, (next_beat_time - current_time) / 2)
                if sleep_time > 0:
                    time.sleep(sleep_time)
    
    def start(self):
        """Start the metronome."""
        with self._lock:
            if self._running:
                return
            
            self._running = True
            self._current_beat = 0
            self._bars_played = 0
            
            self._thread = threading.Thread(target=self._metronome_thread, daemon=True)
            self._thread.start()
    
    def stop(self):
        """Stop the metronome."""
        with self._lock:
            self._running = False
            if self._thread:
                self._thread.join(timeout=1.0)
                self._thread = None
    
    def reset(self):
        """Reset beat counter to beat 1."""
        self._current_beat = 0
        self._bars_played = 0
    
    def tap_tempo(self, tap_times: list):
        """
        Calculate tempo from tap times.
        
        Args:
            tap_times: List of tap timestamps (from time.perf_counter())
        
        Returns:
            Calculated tempo in BPM
        """
        if len(tap_times) < 2:
            return self._tempo
        
        intervals = []
        for i in range(1, len(tap_times)):
            intervals.append(tap_times[i] - tap_times[i-1])
        
        avg_interval = sum(intervals) / len(intervals)
        if avg_interval > 0:
            new_tempo = int(60.0 / avg_interval)
            self._tempo = max(30, min(300, new_tempo))
        
        return self._tempo
