from fastapi import APIRouter, Form, File, UploadFile
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/generate", tags=["Text Generation"])

class GenerateResponse(BaseModel):
    response: str

@router.post("/text")
async def generate_text(
    prompt: str = Form(..., description="Text prompt for generation"),
    max_tokens: int = Form(default=100, description="Maximum tokens to generate"),
    model: str = Form(default="gemini-2.0-flash-exp", description="Model to use"),
    system_prompt: str = Form(default="text_generation", description="System prompt type"),
    custom_system_prompt: str = Form(default="", description="Custom system prompt text"),
    temperature: float = Form(default=0.7, description="Temperature (0.0-2.0)"),
    top_p: float = Form(default=0.9, description="Top-p (0.0-1.0)"),
    files: List[UploadFile] = File(default=[], description="Optional files to include in the prompt")
):
    """Generate text từ prompt"""
    try:
        # Import services
        from ..core import ai_service
        from ..utils.config_manager import ConfigManager
        # Removed cache_manager import as caching is now disabled

        # Get system prompt text using ConfigManager
        if system_prompt == 'custom' and custom_system_prompt.strip():
            system_prompt_text = custom_system_prompt.strip()
        else:
            system_prompts = ConfigManager.get_system_prompts("default")
            system_prompt_text = system_prompts.get(system_prompt,
                "You are a helpful AI assistant. Please provide accurate and helpful responses to user queries.")

        # Process uploaded files
        processed_files = []
        if files:
            import tempfile
            import os
            import mimetypes

            for file in files:
                if file.filename:
                    # Create temporary file
                    suffix = os.path.splitext(file.filename)[1]
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                        content = await file.read()
                        temp_file.write(content)
                        temp_path = temp_file.name

                    # Get MIME type
                    mime_type, _ = mimetypes.guess_type(file.filename)
                    if not mime_type:
                        mime_type = file.content_type or 'application/octet-stream'

                    processed_files.append({
                        'filename': file.filename,
                        'file_path': temp_path,
                        'mime_type': mime_type,
                        'size': len(content)
                    })

        # Generate text
        result = await ai_service.generate_text_with_files(
            prompt=prompt,
            files=processed_files,
            model=model,
            system_prompt=system_prompt_text,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens
        )

        # Clean up temporary files
        for file_info in processed_files:
            try:
                os.unlink(file_info['file_path'])
            except:
                pass

        if result["success"]:
            generated_text = result["generated_text"]

            # ✨ Caching disabled - return response directly
            print(f"✅ Text generation completed (caching disabled)")
            print(f"   Content length: {len(generated_text)} chars")
            
            return GenerateResponse(response=generated_text)
        else:
            return GenerateResponse(response=f"Error: {result.get('error', 'Unknown error')}")

    except Exception as e:
        return GenerateResponse(response=f"Error: {str(e)}")

