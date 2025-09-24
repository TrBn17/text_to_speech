"""
Gemini File Uploader - Single responsibility: Handle file uploads for Gemini API
"""
import os
import pathlib
from typing import Dict, Any, List, Optional, Union

try:
    from google import genai
    from google.genai import types
except ImportError:
    try:
        import google.generativeai as genai
        types = None
    except ImportError:
        genai = None
        types = None


class GeminiFileUploader:
    """Handles file uploads for Gemini API - only file upload logic"""

    def __init__(self, client: Optional[object] = None, legacy_mode: bool = False):
        self.client = client
        self.legacy_mode = legacy_mode

    def upload_file(self, file_path: str, mime_type: str) -> Dict[str, Any]:
        """Upload a single file to Gemini API"""
        try:
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"File not found: {file_path}"
                }

            if self.legacy_mode:
                # Legacy mode - uses global configuration
                uploaded_file = genai.upload_file(file_path)
                return {
                    "success": True,
                    "file": uploaded_file,
                    "method": "legacy_api"
                }
            else:
                # New SDK - requires client and file object
                with open(file_path, 'rb') as f:
                    uploaded_file = self.client.files.upload(file=f, mime_type=mime_type)
                return {
                    "success": True,
                    "file": uploaded_file,
                    "method": "new_api"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"File upload failed: {str(e)}",
                "method": "legacy" if self.legacy_mode else "new"
            }

    def create_inline_part(self, file_path: str, mime_type: str) -> Dict[str, Any]:
        """Create inline file part for smaller files"""
        try:
            if self.legacy_mode or not types:
                return {
                    "success": False,
                    "error": "Inline parts not supported in legacy mode"
                }

            file_pathlib = pathlib.Path(file_path)
            file_data = file_pathlib.read_bytes()

            part = types.Part.from_bytes(
                data=file_data,
                mime_type=mime_type
            )

            return {
                "success": True,
                "part": part,
                "size": len(file_data)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Inline part creation failed: {str(e)}"
            }

    def decide_upload_method(self, file_path: str, mime_type: str, size_threshold: int = 20 * 1024 * 1024) -> str:
        """Decide whether to use inline or file API based on file size and type"""
        try:
            file_size = os.path.getsize(file_path)

            # Always use file API for large files
            if file_size > size_threshold:
                return "file_api"

            # Use inline for images and small PDFs
            if mime_type.startswith('image/') or mime_type == 'application/pdf':
                return "inline"

            # Use file API for other document types
            return "file_api"

        except Exception:
            # Default to file API if unable to determine
            return "file_api"

    def get_upload_limits(self) -> Dict[str, int]:
        """Get upload limits for different file types"""
        return {
            "max_file_size": 50 * 1024 * 1024,  # 50MB
            "inline_threshold": 20 * 1024 * 1024,  # 20MB
            "max_files_per_request": 10
        }