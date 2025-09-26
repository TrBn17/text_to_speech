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

    def upload_multiple_files(self, file_paths: List[str], mime_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """Upload multiple files to Gemini API"""
        try:
            if not file_paths:
                return {
                    "success": False,
                    "error": "No files provided for upload"
                }

            # Validate file count limit
            limits = self.get_upload_limits()
            if len(file_paths) > limits["max_files_per_request"]:
                return {
                    "success": False,
                    "error": f"Too many files. Maximum {limits['max_files_per_request']} files allowed per request"
                }

            uploaded_files = []
            failed_files = []
            total_size = 0

            # If mime_types not provided, try to detect them
            if not mime_types:
                mime_types = [self._detect_mime_type(path) for path in file_paths]
            elif len(mime_types) != len(file_paths):
                return {
                    "success": False,
                    "error": "Number of mime_types must match number of file_paths"
                }

            # Upload each file
            for i, file_path in enumerate(file_paths):
                mime_type = mime_types[i] if i < len(mime_types) else self._detect_mime_type(file_path)
                
                # Check file size before upload
                try:
                    file_size = os.path.getsize(file_path)
                    total_size += file_size
                    
                    if file_size > limits["max_file_size"]:
                        failed_files.append({
                            "file_path": file_path,
                            "error": f"File too large: {file_size} bytes (max: {limits['max_file_size']} bytes)"
                        })
                        continue
                        
                except OSError as e:
                    failed_files.append({
                        "file_path": file_path,
                        "error": f"Cannot access file: {str(e)}"
                    })
                    continue

                # Upload the file
                result = self.upload_file(file_path, mime_type)
                
                if result["success"]:
                    uploaded_files.append({
                        "file_path": file_path,
                        "file": result["file"],
                        "method": result["method"],
                        "mime_type": mime_type,
                        "size": file_size
                    })
                else:
                    failed_files.append({
                        "file_path": file_path,
                        "error": result["error"]
                    })

            # Return results
            success = len(uploaded_files) > 0
            
            return {
                "success": success,
                "uploaded_files": uploaded_files,
                "failed_files": failed_files,
                "summary": {
                    "total_files": len(file_paths),
                    "successful_uploads": len(uploaded_files),
                    "failed_uploads": len(failed_files),
                    "total_size": total_size
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Multiple file upload failed: {str(e)}",
                "uploaded_files": [],
                "failed_files": []
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

    def create_multiple_inline_parts(self, file_paths: List[str], mime_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create inline parts for multiple smaller files"""
        try:
            if self.legacy_mode or not types:
                return {
                    "success": False,
                    "error": "Inline parts not supported in legacy mode"
                }

            if not file_paths:
                return {
                    "success": False,
                    "error": "No files provided for inline parts creation"
                }

            # If mime_types not provided, detect them
            if not mime_types:
                mime_types = [self._detect_mime_type(path) for path in file_paths]
            elif len(mime_types) != len(file_paths):
                return {
                    "success": False,
                    "error": "Number of mime_types must match number of file_paths"
                }

            inline_parts = []
            failed_parts = []
            total_size = 0

            for i, file_path in enumerate(file_paths):
                mime_type = mime_types[i]
                result = self.create_inline_part(file_path, mime_type)
                
                if result["success"]:
                    inline_parts.append({
                        "file_path": file_path,
                        "part": result["part"],
                        "mime_type": mime_type,
                        "size": result["size"]
                    })
                    total_size += result["size"]
                else:
                    failed_parts.append({
                        "file_path": file_path,
                        "error": result["error"]
                    })

            success = len(inline_parts) > 0

            return {
                "success": success,
                "inline_parts": inline_parts,
                "failed_parts": failed_parts,
                "summary": {
                    "total_files": len(file_paths),
                    "successful_parts": len(inline_parts),
                    "failed_parts": len(failed_parts),
                    "total_size": total_size
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Multiple inline parts creation failed: {str(e)}",
                "inline_parts": [],
                "failed_parts": []
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

    def _detect_mime_type(self, file_path: str) -> str:
        """Detect MIME type from file extension"""
        extension = pathlib.Path(file_path).suffix.lower()
        
        mime_types = {
            # Images
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.webp': 'image/webp',
            '.svg': 'image/svg+xml',
            '.ico': 'image/x-icon',
            '.tiff': 'image/tiff',
            '.tif': 'image/tiff',
            
            # Documents
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
            '.csv': 'text/csv',
            '.json': 'application/json',
            '.xml': 'application/xml',
            '.html': 'text/html',
            '.htm': 'text/html',
            
            # Microsoft Office
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.ppt': 'application/vnd.ms-powerpoint',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            
            # Audio
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.ogg': 'audio/ogg',
            '.m4a': 'audio/mp4',
            '.aac': 'audio/aac',
            
            # Video
            '.mp4': 'video/mp4',
            '.avi': 'video/x-msvideo',
            '.mov': 'video/quicktime',
            '.wmv': 'video/x-ms-wmv',
            '.flv': 'video/x-flv',
            '.webm': 'video/webm'
        }
        
        return mime_types.get(extension, 'application/octet-stream')

    def batch_upload_with_method_selection(self, file_paths: List[str], 
                                         mime_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """Upload multiple files with automatic method selection (inline vs file API)"""
        try:
            if not file_paths:
                return {
                    "success": False,
                    "error": "No files provided for upload"
                }

            # If mime_types not provided, detect them
            if not mime_types:
                mime_types = [self._detect_mime_type(path) for path in file_paths]
            elif len(mime_types) != len(file_paths):
                return {
                    "success": False,
                    "error": "Number of mime_types must match number of file_paths"
                }

            inline_files = []
            upload_files = []

            # Categorize files by upload method
            for i, file_path in enumerate(file_paths):
                mime_type = mime_types[i]
                upload_method = self.decide_upload_method(file_path, mime_type)
                
                if upload_method == "inline":
                    inline_files.append((file_path, mime_type))
                else:
                    upload_files.append((file_path, mime_type))

            results = {
                "success": True,
                "inline_results": {},
                "upload_results": {},
                "summary": {
                    "total_files": len(file_paths),
                    "inline_files": len(inline_files),
                    "upload_files": len(upload_files)
                }
            }

            # Process inline files
            if inline_files:
                inline_paths = [path for path, _ in inline_files]
                inline_mimes = [mime for _, mime in inline_files]
                results["inline_results"] = self.create_multiple_inline_parts(inline_paths, inline_mimes)
                if not results["inline_results"]["success"] and len(inline_files) == len(file_paths):
                    results["success"] = False

            # Process upload files
            if upload_files:
                upload_paths = [path for path, _ in upload_files]
                upload_mimes = [mime for _, mime in upload_files]
                results["upload_results"] = self.upload_multiple_files(upload_paths, upload_mimes)
                if not results["upload_results"]["success"] and len(upload_files) == len(file_paths):
                    results["success"] = False

            return results

        except Exception as e:
            return {
                "success": False,
                "error": f"Batch upload failed: {str(e)}",
                "inline_results": {},
                "upload_results": {}
            }

    def filter_image_files(self, file_paths: List[str]) -> List[str]:
        """Filter list to include only image files"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.ico', '.tiff', '.tif'}
        return [
            path for path in file_paths 
            if pathlib.Path(path).suffix.lower() in image_extensions
        ]

    def validate_image_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """Validate that all files are images and accessible"""
        valid_files = []
        invalid_files = []
        
        for file_path in file_paths:
            try:
                # Check if file exists
                if not os.path.exists(file_path):
                    invalid_files.append({
                        "file_path": file_path,
                        "error": "File not found"
                    })
                    continue
                
                # Check if it's an image file
                extension = pathlib.Path(file_path).suffix.lower()
                image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.ico', '.tiff', '.tif'}
                
                if extension not in image_extensions:
                    invalid_files.append({
                        "file_path": file_path,
                        "error": f"Not an image file (extension: {extension})"
                    })
                    continue
                
                # Check file size
                file_size = os.path.getsize(file_path)
                limits = self.get_upload_limits()
                
                if file_size > limits["max_file_size"]:
                    invalid_files.append({
                        "file_path": file_path,
                        "error": f"File too large: {file_size} bytes (max: {limits['max_file_size']} bytes)"
                    })
                    continue
                
                valid_files.append(file_path)
                
            except Exception as e:
                invalid_files.append({
                    "file_path": file_path,
                    "error": f"Validation error: {str(e)}"
                })
        
        return {
            "valid_files": valid_files,
            "invalid_files": invalid_files,
            "summary": {
                "total_files": len(file_paths),
                "valid_count": len(valid_files),
                "invalid_count": len(invalid_files)
            }
        }