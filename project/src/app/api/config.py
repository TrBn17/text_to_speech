from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, validator
import json
import os

router = APIRouter(prefix="/config", tags=["Configuration"])

class ModelParameters(BaseModel):
    """Chi tiết parameters cho model"""
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0, description="Độ sáng tạo (0.0-2.0)")
    top_p: Optional[float] = Field(default=0.9, ge=0.0, le=1.0, description="Top-p sampling (0.0-1.0)")
    max_tokens: Optional[int] = Field(default=100, ge=1, le=8192, description="Số token tối đa")

class TTSParameters(BaseModel):
    """Chi tiết parameters cho TTS"""
    voice: Optional[str] = Field(default="alloy", description="Giọng đọc")
    speed: Optional[float] = Field(default=1.0, ge=0.25, le=4.0, description="Tốc độ đọc (0.25-4.0)")
    provider: Optional[str] = Field(default="openai", description="Provider TTS (openai, google, gemini)")

class ConfigRequest(BaseModel):
    model: Optional[str] = Field(default=None, description="Tên model (vd: gpt-3.5-turbo, gemini-2.5-flash)")
    system_prompt: Optional[str] = Field(default=None, description="System prompt cho model")
    model_parameters: Optional[ModelParameters] = Field(default=None, description="Parameters chi tiết cho model")
    tts_parameters: Optional[TTSParameters] = Field(default=None, description="Parameters cho TTS")

    @validator('model')
    def validate_model(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Model name cannot be empty')
        return v.strip() if v else v

class ConfigResponseFormatted(BaseModel):
    """Formatted response for better user readability"""
    current_configuration: Dict[str, Any]
    available_options: Dict[str, Any]
    quick_templates: Dict[str, Any]
    instructions: Dict[str, Any]

class ConfigResponse(BaseModel):
    model: str
    system_prompt: str
    model_parameters: ModelParameters
    tts_parameters: TTSParameters
    available_models: Dict[str, Any] = {}
    templates: Dict[str, Any] = {}

# Load models from config file
def load_models_config():
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "models.json")
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

models_config = load_models_config()

# In-memory config storage (replace with database in production)
current_config = {
    "model": "gpt-3.5-turbo",
    "system_prompt": models_config.get("system_prompts", {}).get("default", {}).get("text_generation", "You are a helpful assistant."),
    "model_parameters": ModelParameters(),
    "tts_parameters": TTSParameters()
}

# Configuration templates
def get_config_templates():
    return {
        "text_only_basic": {
            "model": "gpt-3.5-turbo",
            "system_prompt": "You are a helpful assistant.",
            "model_parameters": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 100
            }
        },
        "text_only_creative": {
            "model": "gpt-4o",
            "system_prompt": "You are a creative writing assistant.",
            "model_parameters": {
                "temperature": 1.2,
                "top_p": 0.95,
                "max_tokens": 500
            }
        },
        "text_only_technical": {
            "model": "gpt-4o",
            "system_prompt": "You are a technical expert and programming assistant.",
            "model_parameters": {
                "temperature": 0.3,
                "top_p": 0.8,
                "max_tokens": 1000
            }
        },
        "tts_only_basic": {
            "tts_parameters": {
                "voice": "alloy",
                "speed": 1.0,
                "provider": "openai"
            }
        },
        "tts_only_expressive": {
            "tts_parameters": {
                "voice": "nova",
                "speed": 1.1,
                "provider": "openai"
            }
        },
        "tts_only_formal": {
            "tts_parameters": {
                "voice": "echo",
                "speed": 0.9,
                "provider": "openai"
            }
        },
        "complete_config": {
            "model": "gpt-3.5-turbo",
            "system_prompt": "You are a helpful assistant.",
            "model_parameters": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 100
            },
            "tts_parameters": {
                "voice": "alloy",
                "speed": 1.0,
                "provider": "openai"
            }
        }
    }

@router.post("/", response_model=ConfigResponse)
async def update_config(request: ConfigRequest):
    """Cập nhật cấu hình model và parameters"""
    try:
        global current_config

        # Update config with new values (only if provided)
        if request.model is not None:
            current_config["model"] = request.model

        if request.system_prompt is not None:
            current_config["system_prompt"] = request.system_prompt

        # Update model parameters if provided
        if request.model_parameters:
            current_config["model_parameters"] = request.model_parameters

        # Update TTS parameters if provided
        if request.tts_parameters:
            current_config["tts_parameters"] = request.tts_parameters

        # Import AI service to get available models
        from ..core import ai_service
        available_models = ai_service.get_available_models()

        return ConfigResponse(
            model=current_config["model"],
            system_prompt=current_config["system_prompt"],
            model_parameters=current_config["model_parameters"],
            tts_parameters=current_config["tts_parameters"],
            available_models=available_models,
            templates=get_config_templates()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Config update failed: {str(e)}")

def format_config_for_user():
    """Format configuration data for better user readability"""
    try:
        from ..core import ai_service
        available_models = ai_service.get_available_models()

        return {
            "current_configuration": {
                "📄 Model Being Used": current_config["model"],
                "💬 System Prompt": current_config["system_prompt"][:100] + "..." if len(current_config["system_prompt"]) > 100 else current_config["system_prompt"],
                "🎛️ Text Generation Settings": {
                    "🌡️ Temperature (Creativity)": f"{current_config['model_parameters'].temperature} (0=focused, 2=creative)",
                    "🎯 Top-P (Nucleus Sampling)": f"{current_config['model_parameters'].top_p} (0-1.0)",
                    "📝 Max Tokens": f"{current_config['model_parameters'].max_tokens} tokens"
                },
                "🎵 Text-to-Speech Settings": {
                    "🎤 Voice": current_config["tts_parameters"].voice,
                    "⚡ Speed": f"{current_config['tts_parameters'].speed}x (0.25-4.0)",
                    "🔧 Provider": current_config["tts_parameters"].provider
                }
            },
            "available_options": {
                "📚 Text Generation Models": {
                    "🔴 OpenAI": list(available_models.get("text_generation", {}).get("openai", {}).keys()),
                    "🟢 Google Gemini": list(available_models.get("text_generation", {}).get("gemini", {}).keys())
                },
                "🎵 Text-to-Speech Options": {
                    "🔴 OpenAI Voices": available_models.get("voices", {}).get("openai_voices", []),
                    "🟢 Google Languages": available_models.get("voices", {}).get("google_languages", [])[:8]  # Show first 8
                }
            },
            "quick_templates": {
                "💡 How to Use": "Choose a template below, or create custom settings",
                "📝 Text Only": {
                    "basic": "Simple assistant (temp=0.7, 100 tokens)",
                    "creative": "Creative writing (temp=1.2, 500 tokens)",
                    "technical": "Programming help (temp=0.3, 1000 tokens)"
                },
                "🎵 Speech Only": {
                    "basic": "Standard voice (alloy, 1.0x speed)",
                    "expressive": "Lively voice (nova, 1.1x speed)",
                    "formal": "Professional voice (echo, 0.9x speed)"
                },
                "🎯 Complete Setup": "Full configuration with both text + speech"
            },
            "instructions": {
                "📋 How to Update": {
                    "1️⃣ Change Model": "POST /config/ with {'model': 'gpt-4o'}",
                    "2️⃣ Change Settings": "POST /config/ with {'model_parameters': {...}}",
                    "3️⃣ Change Voice": "POST /config/ with {'tts_parameters': {...}}",
                    "4️⃣ Use Template": "GET /config/templates, then POST the template data"
                },
                "💡 Pro Tips": {
                    "🌡️ Temperature": "Lower = more focused, Higher = more creative",
                    "🎯 Top-P": "0.9 = balanced, 0.8 = focused, 0.95 = diverse",
                    "📝 Tokens": "1 token ≈ 0.75 words in English",
                    "⚡ Speed": "1.0 = normal, 0.5 = slow, 2.0 = fast"
                }
            }
        }
    except Exception as e:
        return {"error": f"Configuration formatting failed: {str(e)}"}

@router.get("/", response_model=ConfigResponseFormatted)
async def get_config():
    """Lấy cấu hình hiện tại với format dễ đọc cho người dùng"""
    return format_config_for_user()

@router.get("/templates")
async def get_templates():
    """Lấy các mẫu cấu hình có sẵn"""
    return {
        "templates": get_config_templates(),
        "description": "Các mẫu cấu hình có thể sử dụng",
        "usage": "Sao chép một mẫu và sửa đổi theo nhu cầu, sau đó POST lên /config"
    }