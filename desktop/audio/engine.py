"""
Audio engine with ASIO support for low-latency audio I/O.
Uses sounddevice for cross-platform audio with ASIO backend on Windows.
"""
import numpy as np
import sounddevice as sd
from typing import Optional, Callable, List, Dict, Any
import threading
import queue


class AudioEngine:
    """
    Main audio engine handling both input and output with ASIO support.
    Provides low-latency audio for timing practice and metronome/tone generation.
    """
    
    # Bass frequency range for input detection (Hz)
    BASS_FREQ_MIN = 30
    BASS_FREQ_MAX = 400
    
    def __init__(self, 
                 sample_rate: int = 48000,
                 buffer_size: int = 256,
                 input_channels: int = 1,
                 output_channels: int = 2):
        """
        Initialize the audio engine.
        
        Args:
            sample_rate: Sample rate in Hz (48000 recommended for ASIO)
            buffer_size: Buffer size in samples (lower = less latency, 256 is good)
            input_channels: Number of input channels (1 for mono bass)
            output_channels: Number of output channels (2 for stereo)
        """
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.input_channels = input_channels
        self.output_channels = output_channels
        
        self._input_device: Optional[int] = None
        self._output_device: Optional[int] = None
        self._input_stream: Optional[sd.InputStream] = None
        self._output_stream: Optional[sd.OutputStream] = None
        
        self._input_callback: Optional[Callable] = None
        self._audio_queue: queue.Queue = queue.Queue(maxsize=100)
        
        self._running = False
        self._lock = threading.Lock()
        
        # Audio analysis state
        self._noise_threshold = 0.01
        self._last_trigger_time = 0
        self._min_trigger_interval_ms = 50  # Prevent double-triggers
        
        # Initialize with default ASIO device if available
        self._init_asio_devices()
    
    def _init_asio_devices(self):
        """Try to find and set ASIO devices as default."""
        devices = self.get_devices()
        
        # Look for ASIO devices first
        for dev in devices:
            if 'asio' in dev['name'].lower():
                if dev['max_input_channels'] > 0 and self._input_device is None:
                    self._input_device = dev['index']
                if dev['max_output_channels'] > 0 and self._output_device is None:
                    self._output_device = dev['index']
        
        # Fall back to default devices if no ASIO found
        if self._input_device is None:
            try:
                self._input_device = sd.default.device[0]
            except:
                pass
        
        if self._output_device is None:
            try:
                self._output_device = sd.default.device[1]
            except:
                pass
    
    @staticmethod
    def get_devices() -> List[Dict[str, Any]]:
        """Get list of available audio devices."""
        devices = []
        try:
            for i, dev in enumerate(sd.query_devices()):
                devices.append({
                    'index': i,
                    'name': dev['name'],
                    'max_input_channels': dev['max_input_channels'],
                    'max_output_channels': dev['max_output_channels'],
                    'default_samplerate': dev['default_samplerate'],
                    'hostapi': sd.query_hostapis(dev['hostapi'])['name'],
                    'is_asio': 'asio' in sd.query_hostapis(dev['hostapi'])['name'].lower(),
                })
        except Exception as e:
            print(f"Error querying devices: {e}")
        return devices
    
    @staticmethod
    def get_asio_devices() -> List[Dict[str, Any]]:
        """Get only ASIO devices."""
        return [d for d in AudioEngine.get_devices() if d['is_asio']]
    
    @staticmethod
    def get_input_devices() -> List[Dict[str, Any]]:
        """Get devices with input capability."""
        return [d for d in AudioEngine.get_devices() if d['max_input_channels'] > 0]
    
    @staticmethod
    def get_output_devices() -> List[Dict[str, Any]]:
        """Get devices with output capability."""
        return [d for d in AudioEngine.get_devices() if d['max_output_channels'] > 0]
    
    def set_input_device(self, device_index: int):
        """Set the input device by index."""
        with self._lock:
            self._input_device = device_index
            if self._running:
                self._restart_input_stream()
    
    def set_output_device(self, device_index: int):
        """Set the output device by index."""
        with self._lock:
            self._output_device = device_index
            if self._running:
                self._restart_output_stream()
    
    def set_noise_threshold(self, threshold: float):
        """Set the noise threshold for input detection."""
        self._noise_threshold = max(0.001, min(1.0, threshold))
    
    def get_noise_threshold(self) -> float:
        """Get current noise threshold."""
        return self._noise_threshold
    
    def calibrate_noise_floor(self, duration_ms: int = 500) -> float:
        """
        Sample ambient noise to auto-calibrate threshold.
        Returns the detected noise floor level.
        """
        samples = []
        
        def collect_samples(indata, frames, time_info, status):
            samples.append(np.abs(indata).mean())
        
        # Temporarily capture audio
        with sd.InputStream(
            device=self._input_device,
            channels=self.input_channels,
            samplerate=self.sample_rate,
            blocksize=self.buffer_size,
            callback=collect_samples
        ):
            sd.sleep(duration_ms)
        
        if samples:
            noise_floor = np.mean(samples)
            # Set threshold above noise floor with margin
            self._noise_threshold = noise_floor * 2.5 + 0.005
            return noise_floor
        return 0.01
    
    def _input_callback_internal(self, indata, frames, time_info, status):
        """Internal callback for processing input audio."""
        if status:
            print(f"Input status: {status}")
        
        # Calculate RMS and peak levels
        audio_data = indata[:, 0] if indata.ndim > 1 else indata
        rms = np.sqrt(np.mean(audio_data ** 2))
        peak = np.max(np.abs(audio_data))
        
        # Put data in queue for async processing
        try:
            self._audio_queue.put_nowait({
                'data': audio_data.copy(),
                'rms': rms,
                'peak': peak,
                'time': time_info.inputBufferAdcTime if hasattr(time_info, 'inputBufferAdcTime') else 0,
            })
        except queue.Full:
            pass  # Drop if queue is full
        
        # Call user callback if set
        if self._input_callback:
            self._input_callback(audio_data, rms, peak)
    
    def set_input_callback(self, callback: Optional[Callable]):
        """
        Set callback for input audio processing.
        Callback signature: callback(audio_data: np.ndarray, rms: float, peak: float)
        """
        self._input_callback = callback
    
    def start_input(self):
        """Start the input stream."""
        with self._lock:
            if self._input_stream is not None:
                return
            
            try:
                self._input_stream = sd.InputStream(
                    device=self._input_device,
                    channels=self.input_channels,
                    samplerate=self.sample_rate,
                    blocksize=self.buffer_size,
                    callback=self._input_callback_internal,
                )
                self._input_stream.start()
                self._running = True
            except Exception as e:
                print(f"Failed to start input stream: {e}")
                self._input_stream = None
    
    def stop_input(self):
        """Stop the input stream."""
        with self._lock:
            if self._input_stream:
                self._input_stream.stop()
                self._input_stream.close()
                self._input_stream = None
    
    def _restart_input_stream(self):
        """Restart input stream with new settings."""
        self.stop_input()
        self.start_input()
    
    def _restart_output_stream(self):
        """Restart output stream with new settings."""
        # Output is handled by play_audio, no persistent stream needed
        pass
    
    def play_audio(self, audio_data: np.ndarray, blocking: bool = False):
        """
        Play audio data through the output device.
        
        Args:
            audio_data: Audio samples as numpy array (mono or stereo)
            blocking: If True, wait for playback to complete
        """
        # Ensure stereo
        if audio_data.ndim == 1:
            audio_data = np.column_stack([audio_data, audio_data])
        
        try:
            sd.play(audio_data, self.sample_rate, device=self._output_device, blocking=blocking)
        except Exception as e:
            print(f"Playback error: {e}")
    
    def stop_playback(self):
        """Stop any current playback."""
        sd.stop()
    
    def get_latency_info(self) -> Dict[str, float]:
        """Get estimated latency information."""
        input_latency = 0
        output_latency = 0
        
        try:
            if self._input_device is not None:
                dev = sd.query_devices(self._input_device)
                input_latency = dev.get('default_low_input_latency', 0) * 1000  # Convert to ms
            
            if self._output_device is not None:
                dev = sd.query_devices(self._output_device)
                output_latency = dev.get('default_low_output_latency', 0) * 1000
        except:
            pass
        
        buffer_latency = (self.buffer_size / self.sample_rate) * 1000
        
        return {
            'input_latency_ms': input_latency,
            'output_latency_ms': output_latency,
            'buffer_latency_ms': buffer_latency,
            'total_round_trip_ms': input_latency + output_latency + buffer_latency * 2,
        }
    
    def cleanup(self):
        """Clean up all audio resources."""
        self.stop_input()
        self.stop_playback()
        self._running = False
