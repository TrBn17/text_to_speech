"""
Gemini Service - Refactored to follow SRP
Single responsibility: Orchestrate and coordinate Gemini services
"""
from typing import Dict, Any, Optional
from datetime import datetime

from .gemini import (
    GeminiClientFactory,
    GeminiTextService,
    GeminiTTSService,
    GoogleCloudTTSService
)
from ..utils.config_manager import ConfigManager


class GeminiService:
    """Orchestrator for Gemini services - coordinates but doesn't implement business logic"""

    def __init__(self, api_key: Optional[str] = None, google_credentials_path: Optional[str] = None):
        # Create clients using factory
        try:
            client_info = GeminiClientFactory.create_gemini_client(api_key)
            self.client = client_info["client"]
            self.api_key = client_info["api_key"]
            self.legacy_mode = client_info["legacy_mode"]
        except Exception as e:
            raise ImportError(f"Failed to initialize Gemini client: {e}")

        # Initialize specialized services
        self.text_service = GeminiTextService(self.client, self.legacy_mode)
        self.tts_service = GeminiTTSService(self.client, self.legacy_mode)

        # Initialize Google Cloud TTS if available
        google_tts_client = GeminiClientFactory.create_google_tts_client(google_credentials_path)
        self.google_tts_service = GoogleCloudTTSService(google_tts_client) if google_tts_client else None

    async def generate_text_with_files(self, prompt: str, files: list = None, model: str = "gemini-2.0-flash",
                                     system_prompt: str = "", temperature: float = 0.7,
                                     top_p: float = 0.9, max_tokens: int = 100) -> Dict[str, Any]:
        """Delegate text generation with files to specialized service"""
        if files:
            return await self.text_service.generate_text_with_files(
                prompt=prompt, files=files, model=model, system_prompt=system_prompt,
                temperature=temperature, max_tokens=max_tokens)
        else:
            return await self.text_service.generate_text_only(
                prompt=prompt, model=model, system_prompt=system_prompt,
                temperature=temperature, max_tokens=max_tokens)

    async def generate_text(self, prompt: str, model: str = "gemini-2.0-flash",
                           system_prompt: str = "", temperature: float = 0.7,
                           top_p: float = 0.95, max_tokens: int = 100) -> Dict[str, Any]:
        """Delegate text generation to specialized service"""
        return await self.text_service.generate_text_only(
            prompt=prompt, model=model, system_prompt=system_prompt,
            temperature=temperature, max_tokens=max_tokens)

    async def text_to_speech_gemini(self, text: str, voice_config: Dict[str, Any] = None,
                                   model: str = "gemini-2.5-flash-preview-tts",
                                   prompt_prefix: str = "") -> Dict[str, Any]:
        """Delegate Gemini TTS to specialized service"""
        return await self.tts_service.text_to_speech(
            text=text, voice_config=voice_config, model=model, prompt_prefix=prompt_prefix)

    async def text_to_speech_google(self, text: str, voice: str = "en-US-Neural2-A",
                                   language_code: str = "en-US") -> Dict[str, Any]:
        """Delegate Google Cloud TTS to specialized service"""
        if not self.google_tts_service:
            return {
                "success": False,
                "error": "Google Cloud TTS service not available",
                "text": text,
                "voice": voice,
                "timestamp": datetime.now().isoformat()
            }

        return await self.google_tts_service.text_to_speech(
            text=text, voice=voice, language_code=language_code)

    def get_available_models(self) -> Dict[str, Any]:
        """Get available Gemini models from configuration using ConfigManager"""
        # Get text generation models
        gemini_text_models = list(ConfigManager.get_models_by_provider("gemini", "text_generation").keys())

        # Get TTS models
        gemini_tts_models = []
        google_tts_config = ConfigManager.get_tts_models_by_provider("google")
        for model_id, model_info in google_tts_config.items():
            if model_info.get("type") == "gemini_native":
                gemini_tts_models.append(model_id)

        models = {
            "text_generation": gemini_text_models,
            "text_to_speech": gemini_tts_models
        }

        # Get voices from config
        voices_config = ConfigManager.get_voices_config()
        if "gemini_voices" in voices_config:
            models["gemini_voices"] = voices_config["gemini_voices"]
        if "google_languages" in voices_config:
            models["google_tts_voices"] = voices_config["google_languages"]

        return models