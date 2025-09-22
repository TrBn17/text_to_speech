from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import config_router, generate_router, tts_router
from .api.models import router as models_router
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="Text-to-Speech & Text Generation API",
    description="API cho text generation và text-to-speech với user customization",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with /api prefix
app.include_router(config_router, prefix="/api")
app.include_router(generate_router, prefix="/api")
app.include_router(tts_router, prefix="/api")
app.include_router(models_router, prefix="/api")

@app.get("/")
async def root():
    return {
        "message": "Text-to-Speech & Text Generation API",
        "version": "1.0.0",
        "endpoints": [
            "/api/config",
            "/api/generate",
            "/api/tts",
            "/api/models"
        ],
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "text-to-speech-api"}

