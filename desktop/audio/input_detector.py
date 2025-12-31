"""
Audio input detector for timing practice.
Detects bass note onsets with configurable threshold and latency compensation.
"""
import numpy as np
import time
from typing import Optional, Callable, Dict, Any
from .engine import AudioEngine


class InputDetector:
    """
    Detects audio input (note onsets) for timing practice games.
    Optimized for bass guitar frequency range with ASIO low-latency input.
    """
    
    def __init__(self, audio_engine: AudioEngine):
        """
        Initialize input detector.
        
        Args:
            audio_engine: AudioEngine instance for audio input
        """
        self.audio = audio_engine
        self.sample_rate = audio_engine.sample_rate
        
        # Detection settings
        self._threshold = 0.015
        self._min_trigger_interval_ms = 50  # Prevent double-triggers
        self._last_trigger_time = 0
        
        # Latency compensation
        self._latency_offset_ms = 0
        self._human_reaction_baseline_ms = 140  # Average human reaction time
        
        # Detection state
        self._enabled = False
        self._detecting = False
        
        # Callbacks
        self._note_callback: Optional[Callable] = None
        self._level_callback: Optional[Callable] = None
        
        # Statistics
        self._trigger_count = 0
        self._peak_level = 0.0
    
    @property
    def threshold(self) -> float:
        return self._threshold
    
    @threshold.setter
    def threshold(self, value: float):
        self._threshold = max(0.001, min(1.0, value))
    
    @property
    def latency_offset_ms(self) -> float:
        return self._latency_offset_ms
    
    @latency_offset_ms.setter
    def latency_offset_ms(self, value: float):
        self._latency_offset_ms = max(-100, min(100, value))
    
    def set_note_callback(self, callback: Optional[Callable]):
        """
        Set callback for note detection.
        Callback signature: callback(trigger_time_ms: float, level: float)
        """
        self._note_callback = callback
    
    def set_level_callback(self, callback: Optional[Callable]):
        """
        Set callback for continuous level monitoring.
        Callback signature: callback(rms: float, peak: float)
        """
        self._level_callback = callback
    
    def _process_audio(self, audio_data: np.ndarray, rms: float, peak: float):
        """Process incoming audio and detect note onsets."""
        current_time = time.perf_counter() * 1000  # Convert to ms
        
        # Call level callback for visualization
        if self._level_callback:
            try:
                self._level_callback(rms, peak)
            except Exception as e:
                print(f"Level callback error: {e}")
        
        # Track peak level
        if peak > self._peak_level:
            self._peak_level = peak
        
        if not self._detecting:
            return
        
        # Check if signal exceeds threshold
        if rms > self._threshold:
            # Check minimum interval between triggers
            time_since_last = current_time - self._last_trigger_time
            
            if time_since_last >= self._min_trigger_interval_ms:
                # Apply latency offset
                adjusted_time = current_time - self._latency_offset_ms
                
                self._last_trigger_time = current_time
                self._trigger_count += 1
                
                # Call note callback
                if self._note_callback:
                    try:
                        self._note_callback(adjusted_time, rms)
                    except Exception as e:
                        print(f"Note callback error: {e}")
    
    def start(self):
        """Start audio input detection."""
        self._enabled = True
        self._detecting = True
        self._trigger_count = 0
        self._peak_level = 0.0
        
        # Set our callback on the audio engine
        self.audio.set_input_callback(self._process_audio)
        self.audio.start_input()
    
    def stop(self):
        """Stop audio input detection."""
        self._detecting = False
        self._enabled = False
        self.audio.set_input_callback(None)
        self.audio.stop_input()
    
    def pause(self):
        """Pause detection without stopping input stream."""
        self._detecting = False
    
    def resume(self):
        """Resume detection."""
        self._detecting = True
    
    def calibrate_threshold(self, duration_ms: int = 1000) -> Dict[str, float]:
        """
        Calibrate detection threshold based on ambient noise.
        
        Args:
            duration_ms: Duration to sample ambient noise
        
        Returns:
            Dict with noise_floor, suggested_threshold
        """
        noise_floor = self.audio.calibrate_noise_floor(duration_ms)
        suggested_threshold = noise_floor * 3.0 + 0.01
        
        self._threshold = suggested_threshold
        
        return {
            'noise_floor': noise_floor,
            'suggested_threshold': suggested_threshold,
        }
    
    def calibrate_latency(self, 
                          metronome_times: list, 
                          trigger_times: list) -> Dict[str, float]:
        """
        Calibrate latency offset based on metronome clicks and user responses.
        
        The user plays along with metronome clicks, and we calculate the
        average offset between expected beats and actual triggers.
        
        Args:
            metronome_times: List of metronome click timestamps (ms)
            trigger_times: List of corresponding trigger timestamps (ms)
        
        Returns:
            Dict with average_offset, suggested_latency_offset
        """
        if len(metronome_times) < 3 or len(trigger_times) < 3:
            return {
                'average_offset': 0,
                'suggested_latency_offset': 0,
                'sample_count': 0,
            }
        
        # Match triggers to closest metronome click
        offsets = []
        for trigger_time in trigger_times:
            # Find closest metronome click
            closest_click = min(metronome_times, key=lambda t: abs(t - trigger_time))
            offset = trigger_time - closest_click
            
            # Only use reasonable offsets (-500ms to +500ms)
            if -500 <= offset <= 500:
                offsets.append(offset)
        
        if not offsets:
            return {
                'average_offset': 0,
                'suggested_latency_offset': 0,
                'sample_count': 0,
            }
        
        # Calculate average offset
        avg_offset = sum(offsets) / len(offsets)
        
        # Subtract human reaction time to get system latency
        # If average offset is positive, user is late (add latency compensation)
        # If negative, user is early (subtract latency compensation)
        system_offset = avg_offset - self._human_reaction_baseline_ms
        
        self._latency_offset_ms = system_offset
        
        return {
            'average_offset': avg_offset,
            'suggested_latency_offset': system_offset,
            'sample_count': len(offsets),
        }
    
    def measure_reaction_time(self, 
                              beep_time: float, 
                              trigger_time: float) -> float:
        """
        Measure reaction time from a single beep-response pair.
        
        Args:
            beep_time: Time when beep was played (ms)
            trigger_time: Time when response was detected (ms)
        
        Returns:
            Reaction time in ms
        """
        return trigger_time - beep_time
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get detection statistics."""
        return {
            'trigger_count': self._trigger_count,
            'peak_level': self._peak_level,
            'threshold': self._threshold,
            'latency_offset_ms': self._latency_offset_ms,
            'is_detecting': self._detecting,
        }
    
    def reset_statistics(self):
        """Reset detection statistics."""
        self._trigger_count = 0
        self._peak_level = 0.0
