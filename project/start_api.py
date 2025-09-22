#!/usr/bin/env python3
"""
Simple script to start the Text-to-Speech API
"""
import uvicorn
from src.app.main import app

if __name__ == "__main__":
    print("🚀 Starting Text-to-Speech API...")
    print("📝 Available endpoints:")
    print("  - GET  /           - API info")
    print("  - GET  /health     - Health check")
    print("  - POST /config     - Update config (model, top_p, system_prompt)")
    print("  - GET  /config     - Get current config")
    print("  - POST /generate/text - Generate text from prompt")
    print("  - POST /tts        - Convert text to speech")
    print("  - GET  /docs       - API documentation")
    print()

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )