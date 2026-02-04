"""Utility modules for the voice agents backend."""

from .audio import (
    AudioConfig,
    AudioBuffer,
    VoiceActivityDetector,
    decode_audio_chunk,
    encode_audio_chunk,
    resample_audio,
    convert_int16_to_float32,
    convert_float32_to_int16
)

from .session import (
    SessionState,
    SessionData,
    SessionManager,
    session_manager
)

__all__ = [
    # Audio utilities
    "AudioConfig",
    "AudioBuffer", 
    "VoiceActivityDetector",
    "decode_audio_chunk",
    "encode_audio_chunk",
    "resample_audio",
    "convert_int16_to_float32",
    "convert_float32_to_int16",
    # Session utilities
    "SessionState",
    "SessionData",
    "SessionManager",
    "session_manager"
]
