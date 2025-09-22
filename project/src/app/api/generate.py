from fastapi import APIRouter, HTTPException, Form, File, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import json
import asyncio

router = APIRouter(prefix="/generate", tags=["Text Generation"])

class GenerateResponse(BaseModel):
    success: bool
    generated_text: str
    model_used: str
    config_used: Dict[str, Any]
    usage: Dict[str, Any] = {}
    file_info: List[Dict[str, Any]] = []
    error: str = ""

@router.post("/text")
async def generate_text(
    prompt: str = Form(..., description="Text prompt for generation"),
    max_tokens: int = Form(default=100, description="Maximum tokens to generate"),
    stream: bool = Form(default=False, description="Enable streaming response"),
    files: List[UploadFile] = File(default=[], description="Optional files (PDF, DOCX, images)")
):
    """Generate text từ prompt với support cho file upload và streaming"""
    try:
        # Import services
        from .config import current_config
        from src.app.core import ai_service
        from src.app.core.file_processor import file_processor

        # Process uploaded files
        file_contents = []
        file_info = []

        if files:
            for file in files:
                if file.filename:
                    file_content = await file.read()
                    processed = await file_processor.process_file(file_content, file.filename)
                    file_info.append({
                        "filename": file.filename,
                        "success": processed["success"],
                        "content_length": len(processed.get("content", "")),
                        "file_type": processed.get("file_type", "unknown")
                    })

                    if processed["success"] and processed.get("content"):
                        file_contents.append(f"[File: {file.filename}]\n{processed['content']}")

        # Combine prompt with file contents
        full_prompt = prompt
        if file_contents:
            full_prompt = f"{prompt}\n\n[Attached Files Content]\n" + "\n\n".join(file_contents)

        # Get model parameters
        model_params = current_config.get("model_parameters", {})

        if stream:
            # Return streaming response
            return StreamingResponse(
                generate_text_stream(
                    full_prompt, max_tokens, current_config, model_params, file_info
                ),
                media_type="text/plain"
            )
        else:
            # Regular response
            result = await ai_service.generate_text(
                prompt=full_prompt,
                model=current_config["model"],
                system_prompt=current_config["system_prompt"],
                temperature=model_params.temperature if hasattr(model_params, 'temperature') else 0.7,
                top_p=model_params.top_p if hasattr(model_params, 'top_p') else 0.9,
                max_tokens=max_tokens
            )

            return GenerateResponse(
                success=result["success"],
                generated_text=result["generated_text"],
                model_used=result["model"],
                config_used=current_config,
                usage=result.get("usage", {}),
                file_info=file_info,
                error=result.get("error", "")
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating text: {str(e)}"
        )

async def generate_text_stream(prompt: str, max_tokens: int, config: Dict[str, Any],
                               model_params: Dict[str, Any], file_info: List[Dict[str, Any]]):
    """Generator function for streaming text response"""
    try:
        from src.app.core import ai_service

        # Send file info first if available
        if file_info:
            yield f"data: {json.dumps({'type': 'file_info', 'files': file_info})}\n\n"

        # Send config info
        yield f"data: {json.dumps({'type': 'config', 'model': config['model']})}\n\n"

        # Generate text with streaming
        result = await ai_service.generate_text_stream(
            prompt=prompt,
            model=config["model"],
            system_prompt=config["system_prompt"],
            temperature=model_params.temperature if hasattr(model_params, 'temperature') else 0.7,
            top_p=model_params.top_p if hasattr(model_params, 'top_p') else 0.9,
            max_tokens=max_tokens
        )

        # Stream the response
        if result["success"]:
            async for chunk in result["stream"]:
                yield f"data: {json.dumps({'type': 'content', 'content': chunk})}\n\n"
                await asyncio.sleep(0.01)  # Small delay for better UX

            yield f"data: {json.dumps({'type': 'done', 'usage': result.get('usage', {})})}\n\n"
        else:
            yield f"data: {json.dumps({'type': 'error', 'error': result.get('error', 'Unknown error')})}\n\n"

    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"