"""
Audio Utils - Single responsibility: Handle audio processing operations
Consolidates duplicate audio encoding and duration calculation logic
"""
import base64
import io
import mimetypes
from typing import Dict, Any, Optional, Union


class AudioUtils:
    """Utilities for audio processing operations"""

    @staticmethod
    def encode_audio_base64(audio_data: Union[bytes, bytearray]) -> str:
        """Convert audio data to base64 string"""
        try:
            if isinstance(audio_data, (bytes, bytearray)):
                return base64.b64encode(audio_data).decode('utf-8')
            else:
                raise TypeError("Audio data must be bytes or bytearray")
        except Exception as e:
            raise ValueError(f"Failed to encode audio to base64: {e}")

    @staticmethod
    def decode_audio_base64(audio_base64: str) -> bytes:
        """Convert base64 string back to audio bytes"""
        try:
            return base64.b64decode(audio_base64)
        except Exception as e:
            raise ValueError(f"Failed to decode base64 audio: {e}")

    @staticmethod
    def calculate_duration(text: str, words_per_minute: float = 150.0) -> float:
        """Calculate approximate audio duration based on text length

        Args:
            text: Input text
            words_per_minute: Speaking rate (default: 150 WPM for natural speech)

        Returns:
            Duration in seconds
        """
        if not text or not text.strip():
            return 0.0

        # Method 1: Character-based (current implementation across services)
        # ~80ms per character (as used in existing code)
        char_based_duration = len(text) * 0.08

        # Method 2: Word-based (more accurate)
        word_count = len(text.split())
        word_based_duration = (word_count / words_per_minute) * 60

        # Use character-based for compatibility with existing services
        # TODO: Consider switching to word-based calculation
        return char_based_duration

    @staticmethod
    def get_audio_format_from_mime(mime_type: str) -> str:
        """Extract audio format from MIME type"""
        format_mapping = {
            'audio/mpeg': 'mp3',
            'audio/mp3': 'mp3',
            'audio/wav': 'wav',
            'audio/wave': 'wav',
            'audio/x-wav': 'wav',
            'audio/ogg': 'ogg',
            'audio/webm': 'webm',
            'audio/flac': 'flac',
            'audio/aac': 'aac',
            'audio/opus': 'opus'
        }
        return format_mapping.get(mime_type.lower(), 'unknown')

    @staticmethod
    def get_mime_type_from_format(audio_format: str) -> str:
        """Get MIME type from audio format"""
        format_mapping = {
            'mp3': 'audio/mpeg',
            'wav': 'audio/wav',
            'ogg': 'audio/ogg',
            'webm': 'audio/webm',
            'flac': 'audio/flac',
            'aac': 'audio/aac',
            'opus': 'audio/opus'
        }
        return format_mapping.get(audio_format.lower(), 'application/octet-stream')

    @staticmethod
    def create_audio_blob_url(audio_base64: str, audio_format: str = 'mp3') -> Dict[str, Any]:
        """Create blob URL info for audio data"""
        mime_type = AudioUtils.get_mime_type_from_format(audio_format)
        audio_size = len(base64.b64decode(audio_base64))

        return {
            "base64": audio_base64,
            "mime_type": mime_type,
            "format": audio_format,
            "size_bytes": audio_size,
            "data_url": f"data:{mime_type};base64,{audio_base64}"
        }

    @staticmethod
    def validate_audio_format(audio_format: str) -> bool:
        """Validate if audio format is supported"""
        supported_formats = ['mp3', 'wav', 'ogg', 'webm', 'flac', 'aac', 'opus']
        return audio_format.lower() in supported_formats

    @staticmethod
    def estimate_file_size(text: str, audio_format: str = 'mp3') -> Dict[str, Any]:
        """Estimate audio file size based on text length and format"""
        duration = AudioUtils.calculate_duration(text)

        # Rough bitrate estimates (kbps)
        bitrate_estimates = {
            'mp3': 128,    # Standard MP3
            'wav': 1411,   # CD quality WAV (16-bit, 44.1kHz stereo)
            'ogg': 128,    # Standard OGG
            'flac': 800,   # Lossless FLAC
            'aac': 128,    # Standard AAC
            'opus': 96     # Standard Opus
        }

        bitrate = bitrate_estimates.get(audio_format.lower(), 128)
        estimated_size_bytes = int((duration * bitrate * 1000) / 8)  # Convert kbps to bytes

        return {
            "estimated_duration": duration,
            "estimated_size_bytes": estimated_size_bytes,
            "estimated_size_mb": round(estimated_size_bytes / (1024 * 1024), 2),
            "bitrate_kbps": bitrate,
            "format": audio_format
        }