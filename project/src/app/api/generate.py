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
    model: str = Form(default="gpt-4o-mini", description="Model to use"),
    system_prompt: str = Form(default="text_generation", description="System prompt type"),
    custom_system_prompt: str = Form(default="", description="Custom system prompt text"),
    temperature: float = Form(default=0.7, description="Temperature (0.0-2.0)"),
    top_p: float = Form(default=0.9, description="Top-p (0.0-1.0)"),
    files: List[UploadFile] = File(default=[], description="Optional files (PDF, DOCX, images)")
):
    """Generate text từ prompt với support cho file upload và streaming"""
    try:
        # Import services
        from .config import current_config
        from ..core import ai_service
        from ..utils.file_handler import file_handler
        from ..utils.config_manager import ConfigManager

        # Process uploaded files for LLM-native multimodal input
        processed_files = []
        file_info = []

        print(f"🔍 Files received: {len(files)} files")
        for i, file in enumerate(files):
            print(f"📁 File {i+1}: {file.filename if file.filename else 'no filename'}")

        if files:
            for file in files:
                if file.filename:
                    print(f"📄 Processing file: {file.filename}")
                    file_content = await file.read()
                    print(f"📊 File size: {len(file_content)} bytes")
                    
                    # Save file to static folder first
                    saved_file_info = file_handler.save_uploaded_file(
                        file_content=file_content,
                        filename=file.filename
                    )
                    
                    if saved_file_info["success"]:
                        print(f"💾 File saved to static: {saved_file_info['file_path']}")
                        
                        # Simple file processing without file_processor
                        import mimetypes
                        mime_type, _ = mimetypes.guess_type(file.filename)
                        if not mime_type:
                            # Fallback MIME types
                            file_ext = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
                            mime_map = {
                                'pdf': 'application/pdf',
                                'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                                'doc': 'application/msword',
                                'txt': 'text/plain',
                                'jpg': 'image/jpeg',
                                'jpeg': 'image/jpeg',
                                'png': 'image/png'
                            }
                            mime_type = mime_map.get(file_ext, 'application/octet-stream')

                        print(f"✅ File processed with MIME type: {mime_type}")

                        file_info.append({
                            "filename": file.filename,
                            "success": True,
                            "content_length": len(file_content),
                            "file_type": file.filename.split('.')[-1].lower() if '.' in file.filename else 'unknown',
                            "mime_type": mime_type,
                            "error": ""
                        })

                        # Prepare for multimodal LLM input
                        processed_files.append({
                            "filename": file.filename,
                            "content": file_content,
                            "file_path": saved_file_info["file_path"],
                            "mime_type": mime_type,
                            "preview": ""
                        })
                        print(f"📝 File prepared for LLM: {file.filename}")
                    else:
                        print(f"❌ Failed to save file: {saved_file_info.get('error', 'Unknown error')}")
                        file_info.append({
                            "filename": file.filename,
                            "success": False,
                            "content_length": len(file_content),
                            "file_type": "unknown",
                            "mime_type": "unknown",
                            "error": f"Failed to save file: {saved_file_info.get('error', 'Unknown error')}"
                        })

        print(f"📋 Total files prepared for LLM: {len(processed_files)}")

        # Get system prompt text using ConfigManager
        if system_prompt == 'custom' and custom_system_prompt.strip():
            # Use custom system prompt if provided
            system_prompt_text = custom_system_prompt.strip()
        else:
            # Use predefined system prompt from config
            system_prompts = ConfigManager.get_system_prompts("default")
            system_prompt_text = system_prompts.get(system_prompt,
                "You are a helpful AI assistant. Please provide accurate and helpful responses to user queries.")

        if stream:
            # Return streaming response
            return StreamingResponse(
                generate_text_stream(
                    prompt, processed_files, max_tokens, model, system_prompt_text, temperature, top_p, file_info
                ),
                media_type="text/plain"
            )
        else:
            # Regular response using LLM-native multimodal input
            result = await ai_service.generate_text_with_files(
                prompt=prompt,
                files=processed_files,
                model=model,
                system_prompt=system_prompt_text,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens
            )

            return GenerateResponse(
                success=result["success"],
                generated_text=result["generated_text"],
                model_used=result["model"],
                config_used={
                    "model": model,
                    "system_prompt": system_prompt_text,
                    "temperature": temperature,
                    "top_p": top_p,
                    "max_tokens": max_tokens
                },
                usage=result.get("usage", {}),
                file_info=file_info,
                error=result.get("error", "")
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating text: {str(e)}"
        )

async def generate_text_stream(prompt: str, files: list, max_tokens: int, model: str, system_prompt: str,
                               temperature: float, top_p: float, file_info: List[Dict[str, Any]]):
    """Generator function for streaming text response"""
    try:
        from src.app.core import ai_service

        print(f"🎯 Streaming with model: {model}")

        # Send file info first if available
        if file_info:
            print(f"📁 Sending file info for {len(file_info)} files")
            yield f"data: {json.dumps({'type': 'file_info', 'files': file_info})}\n\n"

        # Send config info
        yield f"data: {json.dumps({'type': 'config', 'model': model})}\n\n"

        # Generate text with streaming - for now fall back to non-streaming for files
        if files:
            # Use regular generation for files (streaming with files needs more complex implementation)
            result = await ai_service.generate_text_with_files(
                prompt=prompt,
                files=files,
                model=model,
                system_prompt=system_prompt,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens
            )
            
            if result["success"]:
                # Send the response as a single chunk for file processing
                yield f"data: {json.dumps({'type': 'content', 'content': result['generated_text']})}\n\n"
                yield f"data: {json.dumps({'type': 'done', 'usage': result.get('usage', {})})}\n\n"
            else:
                print(f"❌ File processing failed: {result.get('error', 'Unknown error')}")
                yield f"data: {json.dumps({'type': 'error', 'error': result.get('error', 'Unknown error')})}\n\n"
        else:
            # Regular streaming for text-only prompts
            result = await ai_service.generate_text_stream(
                prompt=prompt,
                model=model,
                system_prompt=system_prompt,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens
            )

            # Stream the response
            if result["success"]:
                async for chunk in result["stream"]:
                    yield f"data: {json.dumps({'type': 'content', 'content': chunk})}\n\n"
                    await asyncio.sleep(0.01)  # Small delay for better UX

                yield f"data: {json.dumps({'type': 'done', 'usage': result.get('usage', {})})}\n\n"
            else:
                print(f"❌ Streaming failed: {result.get('error', 'Unknown error')}")
                yield f"data: {json.dumps({'type': 'error', 'error': result.get('error', 'Unknown error')})}\n\n"

    except Exception as e:
        print(f"💥 Streaming exception: {str(e)}")
        yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"