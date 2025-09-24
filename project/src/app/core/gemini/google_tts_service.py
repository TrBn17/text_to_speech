"""
Google Cloud TTS Service - Single responsibility: Handle Google Cloud TTS only
"""
from typing import Dict, Any, Optional, List

try:
    from google.cloud import texttospeech
    GOOGLE_TTS_AVAILABLE = True
except ImportError:
    GOOGLE_TTS_AVAILABLE = False
    texttospeech = None

from ...utils.response_builder import ResponseBuilder
from ...utils.audio_utils import AudioUtils


class GoogleCloudTTSService:
    """Handles Google Cloud TTS - only Google TTS logic"""

    def __init__(self, tts_client: Optional[object] = None):
        self.tts_client = tts_client

    async def text_to_speech(self, text: str, voice: str = "en-US-Neural2-A",
                           language_code: str = "en-US") -> Dict[str, Any]:
        """Convert text to speech using Google Cloud TTS"""
        try:
            if not self.tts_client:
                return ResponseBuilder.tts_response(
                    success=False, text=text, voice=voice,
                    error="Google Cloud TTS client not available. Please set up Google Cloud credentials.")

            # Create synthesis input
            synthesis_input = texttospeech.SynthesisInput(text=text)

            # Configure voice selection
            voice_selection = self._create_voice_selection(voice, language_code)

            # Configure audio output
            audio_config = self._create_audio_config()

            # Perform TTS synthesis
            response = self.tts_client.synthesize_speech(
                input=synthesis_input,
                voice=voice_selection,
                audio_config=audio_config
            )

            # Use AudioUtils for consistent processing
            audio_base64 = AudioUtils.encode_audio_base64(response.audio_content)
            duration = AudioUtils.calculate_duration(text)

            return ResponseBuilder.tts_response(
                success=True, text=text, voice=voice, audio_base64=audio_base64,
                audio_format="mp3", duration=duration, language_code=language_code)

        except Exception as e:
            return ResponseBuilder.tts_response(
                success=False, text=text, voice=voice, error=str(e))

    def _create_voice_selection(self, voice: str, language_code: str) -> object:
        """Create voice selection parameters"""
        # Parse voice name to determine gender
        voice_gender = texttospeech.SsmlVoiceGender.FEMALE
        if "male" in voice.lower() or voice.endswith("-B") or voice.endswith("-D"):
            voice_gender = texttospeech.SsmlVoiceGender.MALE

        return texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=voice,
            ssml_gender=voice_gender
        )

    def _create_audio_config(self) -> object:
        """Create audio configuration"""
        return texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )


    def get_available_voices(self) -> List[str]:
        """Get list of available Google Cloud TTS voices - should be loaded from config"""
        # This should ideally be loaded from config, but keeping defaults for now
        # TODO: Pass config to service or load from external source
        return [
            "en-US-Neural2-A", "en-US-Neural2-B", "en-US-Neural2-C",
            "en-US-Neural2-D", "en-US-Neural2-E", "en-US-Neural2-F",
            "en-US-Neural2-G", "en-US-Neural2-H", "en-US-Neural2-I",
            "en-US-Neural2-J", "en-US-Wavenet-A", "en-US-Wavenet-B",
            "en-US-Wavenet-C", "en-US-Wavenet-D", "en-US-Standard-A",
            "en-US-Standard-B", "en-US-Standard-C", "en-US-Standard-D"
        ]

    @staticmethod
    def is_available() -> bool:
        """Check if Google Cloud TTS is available"""
        return GOOGLE_TTS_AVAILABLE