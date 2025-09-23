from typing import Dict, Any, Optional
import os
from datetime import datetime
from ..config.settings import settings

# OpenAI import for TTS only
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

class OpenAITTSService:
    """OpenAI Text-to-Speech service only"""

    def __init__(self, api_key: Optional[str] = None):
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not installed. Install with: pip install openai")

        # Try to get OpenAI API key from: parameter > settings > environment
        self.api_key = (
            api_key or
            getattr(settings.openai, 'api_key', None) or
            os.getenv("OPENAI_API_KEY") or
            os.getenv("OPENAI__API_KEY")
        )
        if not self.api_key:
            raise ValueError("OpenAI API key is required for TTS")

        # Configure OpenAI client
        self.client = openai.OpenAI(api_key=self.api_key)

    async def text_to_speech(self, text: str, voice: str = "alloy",
                             model: str = "tts-1", speed: float = 1.0,
                             instructions: str = "", response_format: str = "mp3") -> Dict[str, Any]:
        """Convert text to speech using OpenAI TTS"""
        try:
            # OpenAI TTS call
            response = self.client.audio.speech.create(
                model=model,
                voice=voice,
                input=text,
                speed=speed,
                response_format=response_format
            )

            # Get audio content
            audio_content = response.content

            return {
                "success": True,
                "audio_content": audio_content,
                "audio_format": response_format,
                "model": model,
                "voice": voice,
                "speed": speed,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "audio_content": None,
                "model": model,
                "timestamp": datetime.now().isoformat()
            }