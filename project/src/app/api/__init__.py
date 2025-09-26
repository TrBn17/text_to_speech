# API routers exports
from .config import router as config_router
from .generate import router as generate_router
from .tts import router as tts_router
from .audio import router as audio_router

__all__ = [
    "config_router",
    "generate_router",
    "tts_router",
    "audio_router"
]
