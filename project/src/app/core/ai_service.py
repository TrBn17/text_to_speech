from typing import Dict, Any, Optional
import json
import os
from ..config.settings import settings
from .openai_service import OpenAIService
from .gemini_service import GeminiService

class AIService:
    """Main service orchestrator for all AI providers"""

    def __init__(self):
        self.openai_service = None
        self.gemini_service = None

        # Load configuration
        self.config = self._load_config()

        # Initialize services if API keys are available
        self._initialize_services()

    def _load_config(self) -> Dict[str, Any]:
        """Load models configuration"""
        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "models.json")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}

    def _initialize_services(self):
        """Initialize AI services based on available API keys"""
        print("🔧 Initializing AI services...")

        # Initialize OpenAI
        try:
            openai_key = getattr(settings.openai, 'api_key', None) or os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI__API_KEY")
            if openai_key:
                self.openai_service = OpenAIService(openai_key)
                print("✅ OpenAI service initialized")
            else:
                print("❌ OpenAI API key not found")
        except Exception:
            print("❌ OpenAI API key not found")

        # Initialize Gemini
        try:
            gemini_key = getattr(settings.gemini, 'api_key', None) or os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI__API_KEY")
            if gemini_key:
                self.gemini_service = GeminiService(gemini_key)
                print("✅ Gemini service initialized")
            else:
                print("❌ Gemini API key not found")
        except Exception:
            print("❌ Gemini API key not found")

        print(f"🎯 Available services: OpenAI={self.openai_service is not None}, Gemini={self.gemini_service is not None}")

    async def generate_text_with_files(self, prompt: str, files: list = None, model: str = "gpt-4o-mini",
                                      system_prompt: str = "", temperature: float = 0.7,
                                      top_p: float = 0.9, max_tokens: int = 100) -> Dict[str, Any]:
        """Generate text with file attachments using appropriate provider"""
        print(f"🤖 AI Service: generate_text_with_files called with model={model}, files={len(files) if files else 0}")

        if model.startswith("gpt") or model.startswith("o1"):
            if not self.openai_service:
                return {"success": False, "error": "OpenAI service not available", "model": model}
            
            return await self.openai_service.generate_text_with_files(
                prompt=prompt, files=files, model=model, system_prompt=system_prompt,
                temperature=temperature, top_p=top_p, max_tokens=max_tokens)
                    
        elif model.startswith("gemini"):
            if not self.gemini_service:
                return {"success": False, "error": "Gemini service not available", "model": model}
            
            return await self.gemini_service.generate_text_with_files(
                prompt=prompt, files=files, model=model, system_prompt=system_prompt,
                temperature=temperature, top_p=top_p, max_tokens=max_tokens)
        else:
            return {"success": False, "error": f"Unknown model: {model}", "model": model}

    async def generate_text(self, prompt: str, model: str = "gpt-4o-mini", system_prompt: str = "",
                           temperature: float = 0.7, top_p: float = 0.9, max_tokens: int = 100) -> Dict[str, Any]:
        """Generate text using the appropriate service based on model"""
        return await self._generate_text_internal(prompt, model, system_prompt, temperature, top_p, max_tokens, stream=False)

    async def generate_text_stream(self, prompt: str, model: str, system_prompt: str = "",
                                  temperature: float = 0.7, top_p: float = 0.9, max_tokens: int = 100) -> Dict[str, Any]:
        """Generate text with streaming using the appropriate service based on model"""
        return await self._generate_text_internal(prompt, model, system_prompt, temperature, top_p, max_tokens, stream=True)

    async def _generate_text_internal(self, prompt: str, model: str, system_prompt: str = "",
                           temperature: float = 0.7, top_p: float = 0.9, max_tokens: int = 100, stream: bool = False) -> Dict[str, Any]:
        """Generate text using the appropriate service based on model"""

        print(f"🚀 Generating text with model: {model}")

        # Determine provider
        if model.startswith(("gpt-", "text-davinci", "text-curie")):
            if not self.openai_service:
                return {"success": False, "error": "OpenAI service not available", "model": model}
            
            if stream:
                return await self.openai_service.generate_text_stream(
                    prompt=prompt, model=model, system_prompt=system_prompt,
                    temperature=temperature, top_p=top_p, max_tokens=max_tokens)
            else:
                return await self.openai_service.generate_text(
                    prompt=prompt, model=model, system_prompt=system_prompt,
                    temperature=temperature, top_p=top_p, max_tokens=max_tokens)
                    
        elif model.startswith("gemini"):
            if not self.gemini_service:
                return {"success": False, "error": "Gemini service not available", "model": model}
            
            if stream:
                return await self.gemini_service.generate_text_stream(
                    prompt=prompt, model=model, system_prompt=system_prompt,
                    temperature=temperature, top_p=top_p, max_tokens=max_tokens)
            else:
                return await self.gemini_service.generate_text(
                    prompt=prompt, model=model, system_prompt=system_prompt,
                    temperature=temperature, top_p=top_p, max_tokens=max_tokens)
        else:
            return {"success": False, "error": f"Unknown model: {model}", "model": model}

    async def text_to_speech(self, text: str, voice: str = "alloy",
                            speed: float = 1.0, provider: str = "openai", 
                            model: str = None, instructions: str = "",
                            voice_config: Dict[str, Any] = None,
                            prompt_prefix: str = "",
                            response_format: str = "mp3") -> Dict[str, Any]:
        """Convert text to speech using the specified provider"""

        if provider == "openai":
            if not self.openai_service:
                return {"success": False, "error": "OpenAI service not available"}
            
            tts_model = model or ("tts-1-hd" if "hd" in voice.lower() else "tts-1")
            return await self.openai_service.text_to_speech(
                text=text, voice=voice, model=tts_model, speed=speed,
                instructions=instructions, response_format=response_format)
                
        elif provider == "gemini":
            if not self.gemini_service:
                return {"success": False, "error": "Gemini service not available"}
            
            tts_model = model or "gemini-2.5-flash-preview-tts"
            return await self.gemini_service.text_to_speech_gemini(
                text=text, voice_config=voice_config or {"voice": voice},
                model=tts_model, prompt_prefix=prompt_prefix)
                
        elif provider == "google":
            if not self.gemini_service:
                return {"success": False, "error": "Gemini service not available"}
            
            return await self.gemini_service.text_to_speech_google(
                text=text, voice=voice)
        else:
            return {"success": False, "error": f"TTS provider '{provider}' not supported"}

    def get_available_models(self) -> Dict[str, Any]:
        """Get all available models from configuration"""
        models = {
            "text_generation": {},
            "text_to_speech": {},
            "voices": {},
            "providers": []
        }

        # Add models from config
        if "text_generation" in self.config:
            models["text_generation"] = self.config["text_generation"]

        if "text_to_speech" in self.config:
            models["text_to_speech"] = self.config["text_to_speech"]

        if "voices" in self.config:
            models["voices"] = self.config["voices"]

        # Add available providers
        if self.openai_service:
            models["providers"].append("openai")
        if self.gemini_service:
            models["providers"].append("gemini")
            models["providers"].append("google")

        return models

    def get_system_prompts(self) -> Dict[str, Any]:
        """Get available system prompts"""
        return self.config.get("system_prompts", {})

    def is_service_available(self, provider: str) -> bool:
        """Check if a specific service is available"""
        if provider == "openai":
            return self.openai_service is not None
        elif provider in ["gemini", "google"]:
            return self.gemini_service is not None
        return False

# Global instance
ai_service = AIService()