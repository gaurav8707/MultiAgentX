"""Audio Processing Utilities for real-time voice streaming."""

import base64
import numpy as np
from typing import Optional


class AudioConfig:
    """Configuration for audio processing."""
    
    # Input audio settings (from browser)
    INPUT_SAMPLE_RATE = 16000
    INPUT_CHANNELS = 1
    INPUT_SAMPLE_WIDTH = 2  # 16-bit audio
    
    # Output audio settings (to browser)
    OUTPUT_SAMPLE_RATE = 24000
    OUTPUT_CHANNELS = 1
    OUTPUT_SAMPLE_WIDTH = 2  # 16-bit audio
    
    # Chunk settings for streaming
    CHUNK_DURATION_MS = 100
    INPUT_CHUNK_SIZE = int(INPUT_SAMPLE_RATE * CHUNK_DURATION_MS / 1000)
    OUTPUT_CHUNK_SIZE = int(OUTPUT_SAMPLE_RATE * CHUNK_DURATION_MS / 1000)


def decode_audio_chunk(base64_audio: str) -> Optional[bytes]:
    """
    Decode base64 encoded audio chunk.
    
    Args:
        base64_audio: Base64 encoded audio data.
        
    Returns:
        Raw audio bytes or None if decoding fails.
    """
    try:
        return base64.b64decode(base64_audio)
    except Exception as e:
        print(f"Error decoding audio: {e}")
        return None


def encode_audio_chunk(audio_bytes: bytes) -> str:
    """
    Encode audio bytes to base64.
    
    Args:
        audio_bytes: Raw audio data.
        
    Returns:
        Base64 encoded string.
    """
    return base64.b64encode(audio_bytes).decode("utf-8")


def convert_int16_to_float32(audio_int16: np.ndarray) -> np.ndarray:
    """Convert int16 audio to float32 normalized to [-1, 1]."""
    return audio_int16.astype(np.float32) / 32768.0


def convert_float32_to_int16(audio_float32: np.ndarray) -> np.ndarray:
    """Convert float32 audio ([-1, 1]) to int16."""
    return (audio_float32 * 32767).astype(np.int16)


def resample_audio(
    audio: np.ndarray, 
    original_rate: int, 
    target_rate: int
) -> np.ndarray:
    """
    Simple linear interpolation resampling.
    For production, consider using librosa or scipy.signal.resample.
    
    Args:
        audio: Input audio array.
        original_rate: Original sample rate.
        target_rate: Target sample rate.
        
    Returns:
        Resampled audio array.
    """
    if original_rate == target_rate:
        return audio
    
    duration = len(audio) / original_rate
    new_length = int(duration * target_rate)
    
    # Simple linear interpolation
    indices = np.linspace(0, len(audio) - 1, new_length)
    resampled = np.interp(indices, np.arange(len(audio)), audio)
    
    return resampled.astype(audio.dtype)


class AudioBuffer:
    """Buffer for accumulating audio chunks."""
    
    def __init__(self, max_size: int = 48000):
        """
        Initialize audio buffer.
        
        Args:
            max_size: Maximum buffer size in samples.
        """
        self.buffer = np.array([], dtype=np.int16)
        self.max_size = max_size
    
    def add(self, audio_chunk: bytes) -> None:
        """Add audio chunk to buffer."""
        chunk_array = np.frombuffer(audio_chunk, dtype=np.int16)
        self.buffer = np.concatenate([self.buffer, chunk_array])
        
        # Trim if exceeds max size
        if len(self.buffer) > self.max_size:
            self.buffer = self.buffer[-self.max_size:]
    
    def get_and_clear(self) -> np.ndarray:
        """Get buffer contents and clear."""
        data = self.buffer.copy()
        self.buffer = np.array([], dtype=np.int16)
        return data
    
    def get_size(self) -> int:
        """Get current buffer size in samples."""
        return len(self.buffer)
    
    def clear(self) -> None:
        """Clear the buffer."""
        self.buffer = np.array([], dtype=np.int16)


class VoiceActivityDetector:
    """Simple energy-based voice activity detection."""
    
    def __init__(
        self, 
        energy_threshold: float = 0.01,
        silence_duration_ms: int = 500,
        sample_rate: int = 16000
    ):
        """
        Initialize VAD.
        
        Args:
            energy_threshold: RMS energy threshold for speech detection.
            silence_duration_ms: Duration of silence to detect end of speech.
            sample_rate: Audio sample rate.
        """
        self.energy_threshold = energy_threshold
        self.silence_samples = int(sample_rate * silence_duration_ms / 1000)
        self.silent_count = 0
        self.is_speaking = False
    
    def process(self, audio_chunk: bytes) -> dict:
        """
        Process audio chunk and detect voice activity.
        
        Args:
            audio_chunk: Raw audio bytes (int16).
            
        Returns:
            Dict with 'is_speech' and 'speech_ended' flags.
        """
        audio = np.frombuffer(audio_chunk, dtype=np.int16).astype(np.float32)
        
        # Calculate RMS energy
        rms = np.sqrt(np.mean(audio ** 2)) / 32768.0
        
        is_speech = rms > self.energy_threshold
        speech_ended = False
        
        if is_speech:
            self.is_speaking = True
            self.silent_count = 0
        else:
            if self.is_speaking:
                self.silent_count += len(audio)
                if self.silent_count >= self.silence_samples:
                    speech_ended = True
                    self.is_speaking = False
                    self.silent_count = 0
        
        return {
            "is_speech": is_speech,
            "speech_ended": speech_ended,
            "rms_energy": rms
        }
    
    def reset(self) -> None:
        """Reset VAD state."""
        self.silent_count = 0
        self.is_speaking = False
