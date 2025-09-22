from typing import Dict, Any, Optional
import os
import base64
from datetime import datetime

# Optional OpenAI import
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None

class OpenAIService:
    def __init__(self, api_key: Optional[str] = None):
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not installed. Install with: pip install openai")

        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI__API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")

        self.client = OpenAI(api_key=self.api_key)

    async def generate_text(self, prompt: str, model: str = "gpt-3.5-turbo",
                           system_prompt: str = "", temperature: float = 0.7,
                           top_p: float = 0.9, max_tokens: int = 100) -> Dict[str, Any]:
        """Generate text using OpenAI models"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p
            )

            return {
                "success": True,
                "generated_text": response.choices[0].message.content,
                "model": model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
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

    async def generate_text_stream(self, prompt: str, model: str = "gpt-3.5-turbo",
                                  system_prompt: str = "", temperature: float = 0.7,
                                  top_p: float = 0.9, max_tokens: int = 100) -> Dict[str, Any]:
        """Generate text using OpenAI models with streaming"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            stream = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stream=True
            )

            async def stream_generator():
                """Generator function for streaming chunks"""
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        yield chunk.choices[0].delta.content

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

    async def text_to_speech(self, text: str, voice: str = "alloy",
                            model: str = "tts-1", speed: float = 1.0) -> Dict[str, Any]:
        """Convert text to speech using OpenAI TTS"""
        try:
            response = self.client.audio.speech.create(
                model=model,
                voice=voice,
                input=text,
                speed=speed,
                response_format="mp3"
            )

            # Convert audio to base64 for easy transport
            audio_data = response.content
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')

            # Calculate approximate duration (rough estimate)
            duration = len(text) * 0.08  # ~80ms per character

            return {
                "success": True,
                "audio_base64": audio_base64,
                "audio_format": "mp3",
                "text": text,
                "voice": voice,
                "model": model,
                "duration": duration,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "text": text,
                "voice": voice,
                "model": model,
                "timestamp": datetime.now().isoformat()
            }

    def get_available_models(self) -> Dict[str, Any]:
        """Get available OpenAI models"""
        return {
            "text_generation": [
                "gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"
            ],
            "text_to_speech": ["tts-1", "tts-1-hd"],
            "voices": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        }