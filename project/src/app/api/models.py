from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any
import json
import os

router = APIRouter(prefix="/models", tags=["Models & Voices"])

def load_models_config():
    """Load models configuration from JSON file"""
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "models.json")
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading models config: {e}")
        return {}

@router.get("/text-generation")
async def get_text_generation_models():
    """Get available text generation models"""
    try:
        models_config = load_models_config()
        text_gen_models = models_config.get("text_generation", {})

        # Flatten the models structure for easier frontend consumption
        models = []

        for provider, provider_models in text_gen_models.items():
            for model_name, model_config in provider_models.items():
                models.append({
                    "id": model_name,
                    "name": model_name,
                    "provider": provider,
                    "max_tokens": model_config.get("max_tokens", model_config.get("max_output_tokens", 4096)),
                    "default_temperature": model_config.get("temperature", 1.0),
                    "default_top_p": model_config.get("top_p", 0.95),
                    "supports_streaming": True,
                    "supports_vision": "gpt-4" in model_name.lower() or "gemini" in model_name.lower()
                })

        return {
            "models": models,
            "total": len(models),
            "providers": list(text_gen_models.keys())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching text generation models: {str(e)}")

@router.get("/tts")
async def get_tts_models():
    """Get available TTS models and voices"""
    try:
        models_config = load_models_config()
        tts_models = models_config.get("text_to_speech", {})
        voices = models_config.get("voices", {})

        # Flatten TTS models
        models = []

        for provider, provider_models in tts_models.items():
            for model_name, model_config in provider_models.items():
                # Determine the actual provider name for display
                if provider == "google":
                    model_type = model_config.get("type", "cloud_tts")
                    if model_type == "gemini_native":
                        display_provider = "Gemini TTS"
                        provider_id = "gemini_tts"
                    else:
                        display_provider = "Google Cloud TTS"
                        provider_id = "google_tts"
                elif provider == "openai":
                    display_provider = "OpenAI TTS"
                    provider_id = "openai_tts"
                else:
                    display_provider = provider.replace("_", " ").title()
                    provider_id = provider

                models.append({
                    "id": model_name,
                    "name": model_name,
                    "provider": display_provider,
                    "provider_id": provider_id,
                    "default_voice": model_config.get("voice", "alloy"),
                    "default_speed": model_config.get("speed", 1.0),
                    "audio_format": model_config.get("response_format",
                                   model_config.get("audio_config", {}).get("audio_encoding", "MP3").lower()),
                    "sample_rate": model_config.get("audio_config", {}).get("sample_rate_hertz", 24000),
                    "type": model_config.get("type", "standard"),
                    "actual_provider": provider  # Keep track of the actual provider for routing
                })

        # Format voices for easy consumption
        available_voices = {
            "openai": voices.get("openai_voices", []),
            "google": [
                {"id": lang, "name": lang, "language": lang.split("-")[0]}
                for lang in voices.get("google_languages", [])
            ]
        }

        return {
            "models": models,
            "voices": available_voices,
            "total_models": len(models),
            "providers": list(tts_models.keys())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching TTS models: {str(e)}")

@router.get("/system-prompts")
async def get_system_prompts():
    """Get available system prompts"""
    try:
        models_config = load_models_config()
        system_prompts = models_config.get("system_prompts", {}).get("default", {})

        prompts = []
        for prompt_id, prompt_text in system_prompts.items():
            prompts.append({
                "id": prompt_id,
                "name": prompt_id.replace("_", " ").title(),
                "text": prompt_text,
                "category": "default"
            })

        return {
            "prompts": prompts,
            "total": len(prompts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching system prompts: {str(e)}")

@router.get("/all")
async def get_all_models():
    """Get all available models, voices, and prompts"""
    try:
        # Get all data
        text_gen_response = await get_text_generation_models()
        tts_response = await get_tts_models()
        prompts_response = await get_system_prompts()

        return {
            "text_generation": text_gen_response,
            "text_to_speech": tts_response,
            "system_prompts": prompts_response,
            "summary": {
                "total_text_models": text_gen_response["total"],
                "total_tts_models": tts_response["total_models"],
                "total_prompts": prompts_response["total"],
                "text_providers": text_gen_response["providers"],
                "tts_providers": tts_response["providers"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching all models: {str(e)}")


@router.get("/tts/prompts")
async def get_tts_prompts():
    """Get available TTS system prompts"""
    try:
        models_config = load_models_config()
        tts_prompts = models_config.get("system_prompts", {}).get("tts_prompts", {})
        
        return {
            "success": True,
            "prompts": tts_prompts,
            "total": len(tts_prompts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching TTS prompts: {str(e)}")

