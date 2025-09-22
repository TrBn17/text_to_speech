"""
Gemini TTS Service - Single responsibility: Handle Gemini native TTS only
"""
from typing import Dict, Any, Optional, List

try:
    from google.genai import types
except ImportError:
    types = None

from ...utils.response_builder import ResponseBuilder
from ...utils.audio_utils import AudioUtils


class GeminiTTSService:
    """Handles Gemini native TTS - only TTS generation logic"""

    def __init__(self, client: Optional[object] = None, legacy_mode: bool = False):
        self.client = client
        self.legacy_mode = legacy_mode

    async def text_to_speech(self, text: str, voice_config: Dict[str, Any] = None,
                           model: str = "gemini-2.5-flash-preview-tts",
                           prompt_prefix: str = "") -> Dict[str, Any]:
        """Convert text to speech using Gemini native TTS"""
        try:
            if self.legacy_mode:
                return ResponseBuilder.tts_response(
                    success=False, text=text, model=model,
                    error="Gemini TTS requires the new Google GenAI SDK")

            if not types or not self.client:
                return ResponseBuilder.tts_response(
                    success=False, text=text, model=model,
                    error="Gemini TTS client not available")

            # Prepare TTS prompt with style control
            full_text = self._prepare_tts_text(text, prompt_prefix)

            # Configure TTS generation
            config = self._create_tts_config(voice_config)

            # Generate audio
            response = self.client.models.generate_content(
                model=model,
                contents=full_text,
                config=config
            )

            # Extract and encode audio data
            audio_data = self._extract_audio_data(response)
            if not audio_data:
                return ResponseBuilder.tts_response(
                    success=False, text=text, model=model,
                    error="No audio data received from Gemini")

            # Use AudioUtils for consistent processing
            audio_base64 = AudioUtils.encode_audio_base64(audio_data)
            duration = AudioUtils.calculate_duration(text)
            voice_name = voice_config.get('voice', 'Kore') if voice_config else 'Kore'

            return ResponseBuilder.tts_response(
                success=True, text=text, model=model, voice=voice_name,
                audio_base64=audio_base64, audio_format="wav", duration=duration)

        except Exception as e:
            return ResponseBuilder.tts_response(
                success=False, text=text, model=model, error=str(e))

    def _prepare_tts_text(self, text: str, prompt_prefix: str) -> str:
        """Prepare text with style control prefix"""
        if prompt_prefix:
            return f"{prompt_prefix}: {text}"
        return text

    def _create_tts_config(self, voice_config: Dict[str, Any] = None) -> object:
        """Create TTS configuration object"""
        default_voice = 'Kore'
        if voice_config and 'voice' in voice_config:
            default_voice = voice_config['voice']

        return types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=default_voice
                    )
                )
            )
        )

    def _extract_audio_data(self, response: object) -> Optional[bytes]:
        """Extract audio data from Gemini response"""
        try:
            return response.candidates[0].content.parts[0].inline_data.data
        except (AttributeError, IndexError):
            return None


    def get_available_voices(self) -> List[str]:
        """Get list of available Gemini TTS voices - should be loaded from config"""
        # This should ideally be loaded from config, but keeping defaults for now
        # TODO: Pass config to service or load from external source
        return [
            "Zephyr", "Puck", "Charon", "Kore", "Fenrir", "Leda",
            "Orus", "Aoede", "Callirrhoe", "Autonoe", "Enceladus",
            "Iapetus", "Umbriel", "Algieba", "Despina", "Erinome",
            "Algenib", "Rasalgethi", "Laomedeia", "Achernar", "Alnilam",
            "Schedar", "Gacrux", "Pulcherrima", "Achird", "Zubenelgenubi",
            "Vindemiatrix", "Sadachbia", "Sadaltager", "Sulafat"
        ]