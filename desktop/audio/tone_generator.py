"""
Tone generator for ear training and audio feedback.
Generates pure tones, intervals, chords, and melodies.
"""
import numpy as np
from typing import List, Optional
from .engine import AudioEngine


class ToneGenerator:
    """
    Generates audio tones for ear training exercises.
    Supports intervals, chords, and melodic patterns.
    """
    
    # Note frequencies (A4 = 440 Hz)
    A4_FREQ = 440.0
    
    # Semitone ratio
    SEMITONE_RATIO = 2 ** (1/12)
    
    # C3 as bass reference (130.81 Hz) - good bass range
    C3_FREQ = 130.81
    
    def __init__(self, audio_engine: AudioEngine):
        """
        Initialize tone generator.
        
        Args:
            audio_engine: AudioEngine instance for audio output
        """
        self.audio = audio_engine
        self.sample_rate = audio_engine.sample_rate
        
        # Default tone settings
        self._base_frequency = self.C3_FREQ
        self._waveform = 'sine'  # sine, triangle, sawtooth
        self._attack = 0.01  # seconds
        self._decay = 0.1
        self._sustain = 0.7
        self._release = 0.2
    
    def set_base_frequency(self, freq: float):
        """Set the base frequency for tone generation."""
        self._base_frequency = max(20, min(2000, freq))
    
    def set_waveform(self, waveform: str):
        """Set waveform type: 'sine', 'triangle', or 'sawtooth'."""
        if waveform in ('sine', 'triangle', 'sawtooth'):
            self._waveform = waveform
    
    def frequency_from_semitones(self, semitones: int, base_freq: Optional[float] = None) -> float:
        """
        Calculate frequency for a note given semitones from base.
        
        Args:
            semitones: Number of semitones above base frequency
            base_freq: Base frequency (defaults to C3)
        
        Returns:
            Frequency in Hz
        """
        base = base_freq or self._base_frequency
        return base * (self.SEMITONE_RATIO ** semitones)
    
    def _generate_waveform(self, frequency: float, duration: float, amplitude: float = 0.7) -> np.ndarray:
        """Generate a waveform at given frequency."""
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        
        if self._waveform == 'sine':
            wave = np.sin(2 * np.pi * frequency * t)
        elif self._waveform == 'triangle':
            wave = 2 * np.abs(2 * (t * frequency - np.floor(t * frequency + 0.5))) - 1
        elif self._waveform == 'sawtooth':
            wave = 2 * (t * frequency - np.floor(t * frequency + 0.5))
        else:
            wave = np.sin(2 * np.pi * frequency * t)
        
        return (wave * amplitude).astype(np.float32)
    
    def _apply_envelope(self, samples: np.ndarray, 
                        attack: Optional[float] = None,
                        decay: Optional[float] = None,
                        sustain: Optional[float] = None,
                        release: Optional[float] = None) -> np.ndarray:
        """Apply ADSR envelope to samples."""
        attack = attack or self._attack
        decay = decay or self._decay
        sustain = sustain or self._sustain
        release = release or self._release
        
        total_samples = len(samples)
        attack_samples = int(attack * self.sample_rate)
        decay_samples = int(decay * self.sample_rate)
        release_samples = int(release * self.sample_rate)
        
        envelope = np.ones(total_samples)
        
        # Attack
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        
        # Decay
        decay_end = attack_samples + decay_samples
        if decay_samples > 0 and decay_end < total_samples:
            envelope[attack_samples:decay_end] = np.linspace(1, sustain, decay_samples)
        
        # Sustain - already at sustain level
        
        # Release
        if release_samples > 0 and total_samples > release_samples:
            envelope[-release_samples:] = np.linspace(sustain, 0, release_samples)
        
        return samples * envelope.astype(np.float32)
    
    def generate_tone(self, 
                      frequency: float,
                      duration: float = 1.0,
                      amplitude: float = 0.7) -> np.ndarray:
        """
        Generate a single tone.
        
        Args:
            frequency: Frequency in Hz
            duration: Duration in seconds
            amplitude: Volume (0.0 to 1.0)
        
        Returns:
            Audio samples as numpy array
        """
        samples = self._generate_waveform(frequency, duration, amplitude)
        return self._apply_envelope(samples)
    
    def generate_note(self,
                      semitones: int,
                      duration: float = 1.0,
                      base_freq: Optional[float] = None) -> np.ndarray:
        """
        Generate a note by semitone offset from base.
        
        Args:
            semitones: Semitones above base frequency
            duration: Duration in seconds
            base_freq: Optional base frequency
        
        Returns:
            Audio samples
        """
        freq = self.frequency_from_semitones(semitones, base_freq)
        return self.generate_tone(freq, duration)
    
    def generate_interval(self,
                          interval_semitones: int,
                          duration_per_note: float = 0.7,
                          gap: float = 0.1,
                          base_freq: Optional[float] = None) -> np.ndarray:
        """
        Generate an interval (two notes played sequentially).
        
        Args:
            interval_semitones: Interval size in semitones
            duration_per_note: Duration of each note
            gap: Gap between notes
            base_freq: Base frequency for root note
        
        Returns:
            Audio samples
        """
        root = self.generate_note(0, duration_per_note, base_freq)
        second = self.generate_note(interval_semitones, duration_per_note, base_freq)
        
        # Add gap between notes
        gap_samples = np.zeros(int(gap * self.sample_rate), dtype=np.float32)
        
        return np.concatenate([root, gap_samples, second])
    
    def generate_chord(self,
                       intervals: List[int],
                       duration: float = 1.5,
                       stagger: float = 0.03,
                       base_freq: Optional[float] = None) -> np.ndarray:
        """
        Generate a chord (multiple notes played together).
        
        Args:
            intervals: List of semitone intervals from root (e.g., [0, 4, 7] for major)
            duration: Duration of the chord
            stagger: Slight delay between note onsets for more natural sound
            base_freq: Base frequency for root note
        
        Returns:
            Audio samples
        """
        base = base_freq or self._base_frequency
        
        # Calculate total duration including stagger
        total_duration = duration + stagger * len(intervals)
        total_samples = int(total_duration * self.sample_rate)
        
        chord = np.zeros(total_samples, dtype=np.float32)
        amplitude_per_note = 0.6 / len(intervals)  # Reduce per-note volume
        
        for i, semitones in enumerate(intervals):
            freq = self.frequency_from_semitones(semitones, base)
            note = self._generate_waveform(freq, duration, amplitude_per_note)
            note = self._apply_envelope(note)
            
            # Apply stagger offset
            offset = int(i * stagger * self.sample_rate)
            end = min(offset + len(note), total_samples)
            chord[offset:end] += note[:end - offset]
        
        # Normalize to prevent clipping
        max_val = np.max(np.abs(chord))
        if max_val > 1.0:
            chord = chord / max_val * 0.9
        
        return chord
    
    def generate_melody(self,
                        intervals: List[int],
                        duration_per_note: float = 0.5,
                        gap: float = 0.05,
                        base_freq: Optional[float] = None) -> np.ndarray:
        """
        Generate a melody (sequence of notes).
        
        Args:
            intervals: List of semitone intervals from base for each note
            duration_per_note: Duration of each note
            gap: Gap between notes
            base_freq: Base frequency
        
        Returns:
            Audio samples
        """
        gap_samples = np.zeros(int(gap * self.sample_rate), dtype=np.float32)
        
        melody_parts = []
        for semitones in intervals:
            note = self.generate_note(semitones, duration_per_note, base_freq)
            melody_parts.append(note)
            melody_parts.append(gap_samples)
        
        return np.concatenate(melody_parts[:-1])  # Remove trailing gap
    
    def play_tone(self, frequency: float, duration: float = 1.0):
        """Play a single tone immediately."""
        samples = self.generate_tone(frequency, duration)
        self.audio.play_audio(samples)
    
    def play_note(self, semitones: int, duration: float = 1.0, base_freq: Optional[float] = None):
        """Play a note by semitone offset."""
        samples = self.generate_note(semitones, duration, base_freq)
        self.audio.play_audio(samples)
    
    def play_interval(self, 
                      interval_semitones: int,
                      duration_per_note: float = 0.7,
                      gap: float = 0.1,
                      base_freq: Optional[float] = None):
        """Play an interval."""
        samples = self.generate_interval(interval_semitones, duration_per_note, gap, base_freq)
        self.audio.play_audio(samples)
    
    def play_chord(self,
                   intervals: List[int],
                   duration: float = 1.5,
                   base_freq: Optional[float] = None):
        """Play a chord."""
        samples = self.generate_chord(intervals, duration, base_freq=base_freq)
        self.audio.play_audio(samples)
    
    def play_melody(self,
                    intervals: List[int],
                    duration_per_note: float = 0.5,
                    base_freq: Optional[float] = None):
        """Play a melody."""
        samples = self.generate_melody(intervals, duration_per_note, base_freq=base_freq)
        self.audio.play_audio(samples)
