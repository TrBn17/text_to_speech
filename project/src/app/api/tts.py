from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
import os

router = APIRouter(prefix="/tts", tags=["Text to Speech"])

class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = "alloy"
    speed: Optional[float] = 1.0
    provider: Optional[str] = "openai"
    model: Optional[str] = None
    # System prompt for TTS style control
    system_prompt: Optional[str] = ""  # Custom instruction cho TTS
    # OpenAI specific parameters
    instructions: Optional[str] = ""  # For OpenAI TTS (newer models)
    response_format: Optional[str] = "mp3"  # mp3, opus, aac, flac, wav, pcm
    # Gemini specific parameters
    prompt_prefix: Optional[str] = ""  # For Gemini TTS style control
    voice_config: Optional[Dict[str, Any]] = None  # For Gemini voice configuration
    # Google Cloud TTS specific
    language_code: Optional[str] = "en-US"  # For Google Cloud TTS

class TTSResponse(BaseModel):
    success: bool
    audio_base64: str = ""
    audio_format: str = ""
    text: str
    voice: str
    duration: float
    provider: str = ""
    model: str = ""
    # Additional parameters used
    speed: float = 1.0
    system_prompt: str = ""
    instructions: str = ""
    prompt_prefix: str = ""
    language_code: str = ""
    available_voices: Dict[str, Any] = {}
    error: str = ""

# Load models from config file
def load_models_config():
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "models.json")
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

models_config = load_models_config()

@router.post("/", response_model=TTSResponse)
async def text_to_audio(request: TTSRequest):
    """Chuyển đổi text thành audio"""
    try:
        # Import AI service and current config
        from src.app.core import ai_service
        from .config import current_config

        # Get TTS parameters from config (handle both Pydantic object and dict)
        tts_params = current_config.get("tts_parameters", {})

        # Extract default values safely
        if hasattr(tts_params, 'voice'):
            # Pydantic object
            default_voice = tts_params.voice
            default_speed = tts_params.speed
            default_provider = tts_params.provider
        elif isinstance(tts_params, dict):
            # Dictionary
            default_voice = tts_params.get('voice', "alloy")
            default_speed = tts_params.get('speed', 1.0)
            default_provider = tts_params.get('provider', "openai")
        else:
            # Default values
            default_voice = "alloy"
            default_speed = 1.0
            default_provider = "openai"

        # Use request parameters if provided, otherwise use config defaults
        voice = request.voice or default_voice
        speed = request.speed or default_speed
        provider = request.provider or default_provider
        model = request.model

        # Handle system prompt for TTS
        system_prompt = request.system_prompt
        if not system_prompt and provider in ["gemini", "google"]:
            # Use default TTS prompt if none provided for Gemini/Google
            tts_prompts = models_config.get("system_prompts", {}).get("tts_prompts", {})
            system_prompt = tts_prompts.get("default", "Read the text naturally with clear pronunciation")

        # Apply system prompt logic based on provider
        instructions = request.instructions
        prompt_prefix = request.prompt_prefix

        if provider == "openai":
            # For OpenAI, use system_prompt as instructions if no instructions provided
            if not instructions and system_prompt:
                instructions = system_prompt
        elif provider in ["gemini", "google"]:
            # For Gemini, use system_prompt as prompt_prefix if no prompt_prefix provided
            if not prompt_prefix and system_prompt:
                prompt_prefix = system_prompt

        # Convert text to speech using AI service
        result = await ai_service.text_to_speech(
            text=request.text,
            voice=voice,
            speed=speed,
            provider=provider,
            model=model,
            instructions=instructions,
            voice_config=request.voice_config,
            prompt_prefix=prompt_prefix,
            response_format=request.response_format
        )

        return TTSResponse(
            success=result["success"],
            audio_base64=result.get("audio_base64", ""),
            audio_format=result.get("audio_format", ""),
            text=result.get("text", request.text),
            voice=result.get("voice", voice),
            duration=result.get("duration", 0.0),
            provider=provider,
            model=result.get("model", model or ""),
            speed=result.get("speed", speed),
            system_prompt=system_prompt,
            instructions=instructions,
            prompt_prefix=prompt_prefix,
            language_code=request.language_code,
            available_voices=models_config.get("voices", {}),
            error=result.get("error", "")
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error converting text to speech: {str(e)}"
        )