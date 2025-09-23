#!/usr/bin/env python3
"""
NotebookLM Automation API endpoint
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import sys
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Add paths for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(current_dir)
core_dir = os.path.join(app_dir, "core")
automation_dir = os.path.join(app_dir, "services", "automation")
flow_dir = os.path.join(core_dir, "flow")

sys.path.append(core_dir)
sys.path.append(automation_dir)
sys.path.append(flow_dir)

from automate import run_notebooklm_automation
from cache_manager import cache_manager, get_latest_text_generation
router = APIRouter()

class NotebookLMRequest(BaseModel):
    cache_key: Optional[str] = "latest"

class NotebookLMResponse(BaseModel):
    success: bool
    message: str
    audio_url: Optional[str] = None
    cache_info: Optional[Dict[str, Any]] = None
    processing_time: Optional[float] = None

@router.post("/notebooklm/generate", response_model=NotebookLMResponse)
async def generate_audio_from_cache(request: NotebookLMRequest):
    """
    Generate audio using NotebookLM automation from cached content.
    Returns audio download URL when completed.
    """
    try:
        start_time = time.time()
        
        # Validate cache exists
        if request.cache_key == "latest":
            cached_content = get_latest_text_generation()
            if not cached_content:
                raise HTTPException(
                    status_code=404,
                    detail="No cached content found. Please generate text content first."
                )
            # Get cache info for response
            latest_cache = cache_manager.get_latest_response('text_generation')
            cache_info = {
                'cache_key': latest_cache.get('cache_key'),
                'content_length': latest_cache.get('content_length'),
                'created_at': latest_cache.get('created_at')
            } if latest_cache else None
        else:
            cached_data = cache_manager.get_response_by_key(request.cache_key)
            if not cached_data:
                raise HTTPException(
                    status_code=404,
                    detail=f"Cache key '{request.cache_key}' not found"
                )
            cache_info = {
                'cache_key': cached_data.get('cache_key'),
                'content_length': cached_data.get('content_length'),
                'created_at': cached_data.get('created_at')
            }
        
        # Run automation in thread pool to avoid sync/async conflict
        print(f"🚀 Starting NotebookLM automation for cache: {request.cache_key}")

        def run_automation():
            return run_notebooklm_automation(
                content_source=request.cache_key,
                debug_mode=False,
                max_wait_minutes=10
            )

        # Execute in thread pool
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            success = await loop.run_in_executor(executor, run_automation)
        
        processing_time = time.time() - start_time
        
        if success:
            # Generate audio URL (simulated - in real implementation you'd track actual download)
            audio_url = f"/downloads/notebooklm_audio_{int(time.time())}.mp3"
            
            return NotebookLMResponse(
                success=True,
                message="Audio generated successfully! Check your Downloads folder.",
                audio_url=audio_url,
                cache_info=cache_info,
                processing_time=processing_time
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="NotebookLM automation failed. Check browser for manual intervention."
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate audio: {str(e)}"
        )