#!/usr/bin/env python3
"""
FoxAI Information API endpoint
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any
import json
import os

router = APIRouter()

class FoxAIInfo(BaseModel):
    name: str
    website: str
    slogan: str
    headquarters: Dict[str, str]
    other_office: Dict[str, str]
    contact: Dict[str, str]
    vision_mission: str
    core_capabilities: List[str]
    target_industries: List[str]
    achievements_metrics: Dict[str, int]
    partners_clients: List[str]
    news_focus: List[str]
    copyright: Dict[str, Any]

@router.get("/foxai/info", response_model=FoxAIInfo)
async def get_foxai_info():
    """
    Get FoxAI company information from support.json file.
    Returns complete information about FOXAI company.
    """
    try:
        # Get the path to support.json
        current_dir = os.path.dirname(os.path.abspath(__file__))
        app_dir = os.path.dirname(current_dir)
        utils_dir = os.path.join(app_dir, "utils")
        support_file = os.path.join(utils_dir, "support.json")

        # Check if file exists
        if not os.path.exists(support_file):
            raise HTTPException(
                status_code=404,
                detail=f"Support file not found at: {support_file}"
            )

        # Read and parse JSON file
        with open(support_file, 'r', encoding='utf-8') as f:
            foxai_data = json.load(f)

        # Validate that all required fields are present
        required_fields = [
            'name', 'website', 'slogan', 'headquarters', 'other_office',
            'contact', 'vision_mission', 'core_capabilities', 'target_industries',
            'achievements_metrics', 'partners_clients', 'news_focus', 'copyright'
        ]

        for field in required_fields:
            if field not in foxai_data:
                raise HTTPException(
                    status_code=500,
                    detail=f"Missing required field '{field}' in support.json"
                )

        return FoxAIInfo(**foxai_data)

    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Invalid JSON format in support.json: {str(e)}"
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="FoxAI support information file not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve FoxAI information: {str(e)}"
        )