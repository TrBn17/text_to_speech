from typing import Dict, Any, Optional
import os
import base64
from datetime import datetime

# Optional Gemini import - New Google GenAI SDK (2024)
try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    # Fallback to legacy library
    try:
        import google.generativeai as genai
        GEMINI_AVAILABLE = True
        LEGACY_GEMINI = True
    except ImportError:
        GEMINI_AVAILABLE = False
        genai = None
        LEGACY_GEMINI = False

# Optional Google Cloud TTS import
try:
    from google.cloud import texttospeech
    GOOGLE_TTS_AVAILABLE = True
except ImportError:
    GOOGLE_TTS_AVAILABLE = False
    texttospeech = None

class GeminiService:
    def __init__(self, api_key: Optional[str] = None, google_credentials_path: Optional[str] = None):
        if not GEMINI_AVAILABLE:
            raise ImportError("Google Generative AI library not installed. Install with: pip install google-genai")

        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI__API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key is required")

        # Configure based on library version
        try:
            # New Google GenAI SDK
            self.client = genai.Client(api_key=self.api_key)
            self.legacy_mode = False
        except (AttributeError, TypeError):
            # Legacy library fallback
            genai.configure(api_key=self.api_key)
            self.client = None
            self.legacy_mode = True

        # Initialize Google Cloud TTS client if credentials and library available
        self.tts_client = None
        if GOOGLE_TTS_AVAILABLE and (google_credentials_path or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")):
            try:
                self.tts_client = texttospeech.TextToSpeechClient()
            except Exception as e:
                print(f"Google TTS client initialization failed: {e}")

    async def generate_text(self, prompt: str, model: str = "gemini-2.0-flash",
                           system_prompt: str = "", temperature: float = 0.7,
                           top_p: float = 0.95, max_tokens: int = 100) -> Dict[str, Any]:
        """Generate text using Gemini models"""
        try:
            if self.legacy_mode:
                # Legacy library approach
                generation_config = genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    top_p=top_p,
                    temperature=temperature,
                )

                model_instance = genai.GenerativeModel(
                    model_name=model,
                    generation_config=generation_config,
                    system_instruction=system_prompt if system_prompt else None
                )

                response = model_instance.generate_content(prompt)
                generated_text = response.text
                usage_data = {
                    "prompt_tokens": response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 0,
                    "completion_tokens": response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0,
                    "total_tokens": response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0
                }
            else:
                # New Google GenAI SDK approach
                contents = prompt
                if system_prompt:
                    contents = f"System: {system_prompt}\n\nUser: {prompt}"

                response = self.client.models.generate_content(
                    model=model,
                    contents=contents,
                    config={
                        "max_output_tokens": max_tokens,
                        "temperature": temperature,
                        "top_p": top_p
                    }
                )
                generated_text = response.text
                usage_data = {
                    "prompt_tokens": getattr(response, 'prompt_token_count', 0),
                    "completion_tokens": getattr(response, 'candidates_token_count', 0),
                    "total_tokens": getattr(response, 'total_token_count', 0)
                }

            return {
                "success": True,
                "generated_text": generated_text,
                "model": model,
                "usage": usage_data,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "generated_text": f"Error generating text: {str(e)}",
                "model": model,
                "timestamp": datetime.now().isoformat()
            }

    async def generate_text_stream(self, prompt: str, model: str = "gemini-2.0-flash",
                                  system_prompt: str = "", temperature: float = 0.7,
                                  top_p: float = 0.95, max_tokens: int = 100) -> Dict[str, Any]:
        """Generate text using Gemini models with streaming"""
        try:
            if self.legacy_mode:
                # Legacy library approach
                generation_config = genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    top_p=top_p,
                    temperature=temperature,
                )

                model_instance = genai.GenerativeModel(
                    model_name=model,
                    generation_config=generation_config,
                    system_instruction=system_prompt if system_prompt else None
                )

                response = model_instance.generate_content(prompt, stream=True)

                async def stream_generator():
                    """Generator function for streaming chunks"""
                    for chunk in response:
                        if chunk.text:
                            yield chunk.text
            else:
                # New Google GenAI SDK approach
                contents = prompt
                if system_prompt:
                    contents = f"System: {system_prompt}\n\nUser: {prompt}"

                response = self.client.models.generate_content(
                    model=model,
                    contents=contents,
                    config={
                        "max_output_tokens": max_tokens,
                        "temperature": temperature,
                        "top_p": top_p
                    },
                    stream=True
                )

                async def stream_generator():
                    """Generator function for streaming chunks"""
                    for chunk in response:
                        if hasattr(chunk, 'text') and chunk.text:
                            yield chunk.text

            return {
                "success": True,
                "stream": stream_generator(),
                "model": model,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            async def error_generator():
                yield f"Error: {str(e)}"

            return {
                "success": False,
                "error": str(e),
                "stream": error_generator(),
                "model": model,
                "timestamp": datetime.now().isoformat()
            }

    async def text_to_speech_gemini(self, text: str, voice_config: Optional[Dict] = None) -> Dict[str, Any]:
        """Convert text to speech using Gemini TTS (if available)"""
        try:
            # This is a placeholder for Gemini TTS API
            # Gemini TTS might not be directly available yet
            return {
                "success": False,
                "error": "Gemini TTS not yet implemented",
                "text": text,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "text": text,
                "timestamp": datetime.now().isoformat()
            }

    async def text_to_speech_google(self, text: str, voice: str = "en-US-Neural2-A",
                                   language_code: str = "en-US") -> Dict[str, Any]:
        """Convert text to speech using Google Cloud TTS"""
        if not GOOGLE_TTS_AVAILABLE:
            return {
                "success": False,
                "error": "Google Cloud TTS library not installed",
                "text": text,
                "timestamp": datetime.now().isoformat()
            }

        if not self.tts_client:
            return {
                "success": False,
                "error": "Google TTS client not initialized",
                "text": text,
                "timestamp": datetime.now().isoformat()
            }

        try:
            # Set the text input to be synthesized
            synthesis_input = texttospeech.SynthesisInput(text=text)

            # Build the voice request
            voice_params = texttospeech.VoiceSelectionParams(
                language_code=language_code,
                name=voice
            )

            # Select the type of audio file you want returned
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                sample_rate_hertz=24000
            )

            # Perform the text-to-speech request
            response = self.tts_client.synthesize_speech(
                input=synthesis_input,
                voice=voice_params,
                audio_config=audio_config
            )

            # Convert audio to base64
            audio_base64 = base64.b64encode(response.audio_content).decode('utf-8')

            # Calculate approximate duration
            duration = len(text) * 0.08

            return {
                "success": True,
                "audio_base64": audio_base64,
                "audio_format": "mp3",
                "text": text,
                "voice": voice,
                "language_code": language_code,
                "duration": duration,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "text": text,
                "voice": voice,
                "timestamp": datetime.now().isoformat()
            }

    def get_available_models(self) -> Dict[str, Any]:
        """Get available Gemini models"""
        return {
            "text_generation": [
                "gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash",
                "gemini-1.0-pro"
            ],
            "text_to_speech": ["gemini-2.0-flash-tts"],
            "google_tts_voices": [
                "en-US-Neural2-A", "en-US-Neural2-B", "en-US-Neural2-C",
                "en-US-Wavenet-A", "en-US-Wavenet-B", "en-US-Standard-A"
            ]
        }