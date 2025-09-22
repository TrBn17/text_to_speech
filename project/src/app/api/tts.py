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

class TTSResponse(BaseModel):
    success: bool
    audio_base64: str = ""
    audio_format: str = ""
    text: str
    voice: str
    duration: float
    provider: str = ""
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

        # Get TTS parameters from config
        tts_params = current_config.get("tts_parameters", {})

        # Use request parameters if provided, otherwise use config defaults
        voice = request.voice or (tts_params.voice if hasattr(tts_params, 'voice') else "alloy")
        speed = request.speed or (tts_params.speed if hasattr(tts_params, 'speed') else 1.0)
        provider = request.provider or (tts_params.provider if hasattr(tts_params, 'provider') else "openai")

        # Convert text to speech using AI service
        result = await ai_service.text_to_speech(
            text=request.text,
            voice=voice,
            speed=speed,
            provider=provider
        )

        return TTSResponse(
            success=result["success"],
            audio_base64=result.get("audio_base64", ""),
            audio_format=result.get("audio_format", ""),
            text=result["text"],
            voice=result.get("voice", voice),
            duration=result.get("duration", 0.0),
            provider=provider,
            available_voices=models_config.get("voices", {}),
            error=result.get("error", "")
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error converting text to speech: {str(e)}"
        )