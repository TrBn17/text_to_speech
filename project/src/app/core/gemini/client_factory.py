"""
Gemini Client Factory - Single responsibility: Create and configure Gemini clients
"""
import os
from typing import Optional, Dict, Any
from ...config.settings import settings

# Optional Gemini imports
try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    try:
        import google.generativeai as genai
        GEMINI_AVAILABLE = True
        LEGACY_GEMINI = True
    except ImportError:
        GEMINI_AVAILABLE = False
        genai = None
        LEGACY_GEMINI = False

try:
    from google.cloud import texttospeech
    GOOGLE_TTS_AVAILABLE = True
except ImportError:
    GOOGLE_TTS_AVAILABLE = False
    texttospeech = None


class GeminiClientFactory:
    """Factory for creating Gemini clients - handles only client creation and configuration"""

    @staticmethod
    def create_gemini_client(api_key: Optional[str] = None) -> Dict[str, Any]:
        """Create Gemini client based on available library version"""
        if not GEMINI_AVAILABLE:
            raise ImportError("Google Generative AI library not installed. Install with: pip install google-genai")

        # Get API key
        resolved_api_key = (
            api_key or
            getattr(settings.gemini, 'api_key', None) or
            os.getenv("GEMINI_API_KEY") or
            os.getenv("GEMINI__API_KEY")
        )

        if not resolved_api_key:
            raise ValueError("Gemini API key is required")

        try:
            # Try new Google GenAI SDK first
            client = genai.Client(api_key=resolved_api_key)
            return {
                "client": client,
                "api_key": resolved_api_key,
                "legacy_mode": False
            }
        except (AttributeError, TypeError):
            # Fallback to legacy library
            genai.configure(api_key=resolved_api_key)
            return {
                "client": None,  # Legacy mode uses global configuration
                "api_key": resolved_api_key,
                "legacy_mode": True
            }

    @staticmethod
    def create_google_tts_client(credentials_path: Optional[str] = None) -> Optional[object]:
        """Create Google Cloud TTS client"""
        if not GOOGLE_TTS_AVAILABLE:
            return None

        if not (credentials_path or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")):
            return None

        try:
            return texttospeech.TextToSpeechClient()
        except Exception as e:
            print(f"Google TTS client initialization failed: {e}")
            return None

    @staticmethod
    def get_availability_info() -> Dict[str, bool]:
        """Get information about available libraries"""
        return {
            "gemini_available": GEMINI_AVAILABLE,
            "google_tts_available": GOOGLE_TTS_AVAILABLE,
            "legacy_mode": getattr(globals(), 'LEGACY_GEMINI', False)
        }