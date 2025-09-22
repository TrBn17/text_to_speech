import os
import uuid
import base64
import tempfile
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import mimetypes
import io

class FileHandler:
    """Utility class for handling file uploads and conversions for AI services"""

    def __init__(self, static_folder: str = None):
        self.static_folder = static_folder or os.path.join(os.path.dirname(__file__), '..', '..', '..', 'static')
        os.makedirs(self.static_folder, exist_ok=True)

        # File cleanup after 1 hour by default
        self.cleanup_after_hours = 1

        # Supported file types
        self.supported_image_types = {
            'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp', 'image/webp'
        }
        self.supported_document_types = {
            'application/pdf', 'text/plain', 'text/csv', 'application/json',
            'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }

        # Max file sizes (in bytes)
        self.max_image_size = 20 * 1024 * 1024  # 20MB for images
        self.max_document_size = 50 * 1024 * 1024  # 50MB for documents (Gemini File API limit)

    def save_uploaded_file(self, file_content: bytes, filename: str, mime_type: str = None) -> Dict[str, Any]:
        """Save uploaded file to static folder and return file info"""
        try:
            # Generate unique filename to avoid conflicts
            file_id = str(uuid.uuid4())
            file_extension = os.path.splitext(filename)[1] if filename else ''
            if not file_extension and mime_type:
                file_extension = mimetypes.guess_extension(mime_type) or ''

            unique_filename = f"{file_id}{file_extension}"
            file_path = os.path.join(self.static_folder, unique_filename)

            # Validate file size
            file_size = len(file_content)
            if mime_type and mime_type in self.supported_image_types:
                if file_size > self.max_image_size:
                    raise ValueError(f"Image file too large: {file_size} bytes (max: {self.max_image_size})")
            elif file_size > self.max_document_size:
                raise ValueError(f"Document file too large: {file_size} bytes (max: {self.max_document_size})")

            # Save file
            with open(file_path, 'wb') as f:
                f.write(file_content)

            # Detect mime type if not provided
            if not mime_type:
                mime_type, _ = mimetypes.guess_type(filename)
                mime_type = mime_type or 'application/octet-stream'

            return {
                'success': True,
                'file_id': file_id,
                'filename': filename,
                'unique_filename': unique_filename,
                'file_path': file_path,
                'mime_type': mime_type,
                'file_size': file_size,
                'created_at': datetime.now().isoformat()
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'filename': filename
            }



    def cleanup_old_files(self):
        """Remove files older than cleanup_after_hours"""
        try:
            current_time = datetime.now()
            cutoff_time = current_time - timedelta(hours=self.cleanup_after_hours)

            for filename in os.listdir(self.static_folder):
                file_path = os.path.join(self.static_folder, filename)
                if os.path.isfile(file_path):
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if file_mtime < cutoff_time:
                        os.remove(file_path)
                        print(f"Cleaned up old file: {filename}")

        except Exception as e:
            print(f"Error during file cleanup: {e}")

    def get_file_info(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a saved file by ID"""
        try:
            for filename in os.listdir(self.static_folder):
                if filename.startswith(file_id):
                    file_path = os.path.join(self.static_folder, filename)
                    if os.path.exists(file_path):
                        stat = os.stat(file_path)
                        mime_type, _ = mimetypes.guess_type(filename)

                        return {
                            'file_id': file_id,
                            'filename': filename,
                            'file_path': file_path,
                            'mime_type': mime_type or 'application/octet-stream',
                            'file_size': stat.st_size,
                            'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                            'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat()
                        }
            return None
        except Exception as e:
            print(f"Error getting file info: {e}")
            return None

    def delete_file(self, file_id: str) -> bool:
        """Delete a file by ID"""
        try:
            for filename in os.listdir(self.static_folder):
                if filename.startswith(file_id):
                    file_path = os.path.join(self.static_folder, filename)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        return True
            return False
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False


# Global file handler instance
file_handler = FileHandler()