from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Dict, Any
import os
import mimetypes
from datetime import datetime
from pathlib import Path

router = APIRouter(tags=["audio"])

# Path to audio downloads directory
AUDIO_DOWNLOADS_DIR = Path(__file__).parent.parent.parent / "static" / "audio_downloads"

@router.get("/audio/files", response_model=List[Dict[str, Any]])
async def list_audio_files():
    """
    List all audio files in the downloads directory with metadata
    """
    try:
        # Ensure directory exists
        AUDIO_DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

        files = []
        for file_path in AUDIO_DOWNLOADS_DIR.iterdir():
            if file_path.is_file():
                # Get file stats
                stat = file_path.stat()

                # Determine MIME type
                mime_type, _ = mimetypes.guess_type(str(file_path))

                files.append({
                    "name": file_path.name,
                    "size": stat.st_size,
                    "size_mb": round(stat.st_size / (1024 * 1024), 2),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "mime_type": mime_type or "application/octet-stream",
                    "is_audio": mime_type and mime_type.startswith("audio/") if mime_type else False,
                    "download_url": f"/api/audio/download/{file_path.name}"
                })

        # Sort by modified time (newest first)
        files.sort(key=lambda x: x["modified"], reverse=True)

        return files

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")

@router.get("/audio/download/{filename}")
async def download_audio_file(filename: str):
    """
    Download a specific audio file
    """
    try:
        file_path = AUDIO_DOWNLOADS_DIR / filename

        # Security check: ensure file is within audio downloads directory
        if not str(file_path.resolve()).startswith(str(AUDIO_DOWNLOADS_DIR.resolve())):
            raise HTTPException(status_code=403, detail="Access denied")

        # Check if file exists
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        # Get MIME type
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if not mime_type:
            mime_type = "application/octet-stream"

        return FileResponse(
            path=str(file_path),
            media_type=mime_type,
            filename=filename
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")

@router.delete("/audio/files/{filename}")
async def delete_audio_file(filename: str):
    """
    Delete a specific audio file
    """
    try:
        file_path = AUDIO_DOWNLOADS_DIR / filename

        # Security check: ensure file is within audio downloads directory
        if not str(file_path.resolve()).startswith(str(AUDIO_DOWNLOADS_DIR.resolve())):
            raise HTTPException(status_code=403, detail="Access denied")

        # Check if file exists
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        # Delete the file
        file_path.unlink()

        return {"message": f"File '{filename}' deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")

@router.get("/audio/stats")
async def get_audio_stats():
    """
    Get statistics about audio files
    """
    try:
        # Ensure directory exists
        AUDIO_DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

        total_files = 0
        total_size = 0
        audio_files = 0
        file_types = {}

        for file_path in AUDIO_DOWNLOADS_DIR.iterdir():
            if file_path.is_file():
                total_files += 1
                file_size = file_path.stat().st_size
                total_size += file_size

                # Check MIME type
                mime_type, _ = mimetypes.guess_type(str(file_path))
                if mime_type and mime_type.startswith("audio/"):
                    audio_files += 1

                # Count file extensions
                ext = file_path.suffix.lower()
                file_types[ext] = file_types.get(ext, 0) + 1

        return {
            "total_files": total_files,
            "audio_files": audio_files,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "file_types": file_types,
            "directory": str(AUDIO_DOWNLOADS_DIR)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

@router.post("/audio/cleanup")
async def cleanup_old_files(days: int = 7):
    """
    Delete files older than specified days
    """
    try:
        # Ensure directory exists
        AUDIO_DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

        cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
        deleted_files = []

        for file_path in AUDIO_DOWNLOADS_DIR.iterdir():
            if file_path.is_file():
                if file_path.stat().st_mtime < cutoff_time:
                    file_name = file_path.name
                    file_path.unlink()
                    deleted_files.append(file_name)

        return {
            "message": f"Cleanup completed",
            "deleted_files": deleted_files,
            "count": len(deleted_files)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during cleanup: {str(e)}")