"""
Response Builder - Single responsibility: Create standardized API responses
Consolidates duplicate response creation logic across all services
"""
from typing import Dict, Any, Optional
from datetime import datetime


class ResponseBuilder:
    """Standardized response builder for all services"""

    @staticmethod
    def success_response(**kwargs) -> Dict[str, Any]:
        """Create a standardized success response"""
        response = {
            "success": True,
            "timestamp": datetime.now().isoformat()
        }
        response.update(kwargs)
        return response

    @staticmethod
    def error_response(error: str, **kwargs) -> Dict[str, Any]:
        """Create a standardized error response"""
        response = {
            "success": False,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        response.update(kwargs)
        return response

    @staticmethod
    def text_generation_response(success: bool, generated_text: str, model: str,
                               error: str = "", usage: Optional[Dict[str, Any]] = None,
                               **kwargs) -> Dict[str, Any]:
        """Create standardized text generation response"""
        if success:
            return ResponseBuilder.success_response(
                generated_text=generated_text,
                model=model,
                usage=usage or {},
                **kwargs
            )
        else:
            return ResponseBuilder.error_response(
                error=error,
                generated_text=f"Error generating text: {error}",
                model=model,
                **kwargs
            )

    @staticmethod
    def tts_response(success: bool, text: str, model: str = "", voice: str = "",
                    audio_base64: str = "", audio_format: str = "", duration: float = 0.0,
                    error: str = "", **kwargs) -> Dict[str, Any]:
        """Create standardized TTS response"""
        if success:
            return ResponseBuilder.success_response(
                audio_base64=audio_base64,
                audio_format=audio_format,
                text=text,
                voice=voice,
                model=model,
                duration=duration,
                **kwargs
            )
        else:
            return ResponseBuilder.error_response(
                error=error,
                text=text,
                voice=voice,
                model=model,
                **kwargs
            )

    @staticmethod
    def config_response(success: bool, config_data: Optional[Dict[str, Any]] = None,
                       error: str = "", **kwargs) -> Dict[str, Any]:
        """Create standardized configuration response"""
        if success:
            return ResponseBuilder.success_response(
                **(config_data or {}),
                **kwargs
            )
        else:
            return ResponseBuilder.error_response(
                error=error,
                **kwargs
            )

    @staticmethod
    def file_processing_response(success: bool, filename: str, error: str = "",
                               file_info: Optional[Dict[str, Any]] = None,
                               **kwargs) -> Dict[str, Any]:
        """Create standardized file processing response"""
        if success:
            return ResponseBuilder.success_response(
                filename=filename,
                **(file_info or {}),
                **kwargs
            )
        else:
            return ResponseBuilder.error_response(
                error=error,
                filename=filename,
                **kwargs
            )

    @staticmethod
    def health_check_response(healthy: bool, services_status: Optional[Dict[str, bool]] = None,
                            error: str = "", **kwargs) -> Dict[str, Any]:
        """Create standardized health check response"""
        if healthy:
            return ResponseBuilder.success_response(
                status="healthy",
                services=services_status or {},
                **kwargs
            )
        else:
            return ResponseBuilder.error_response(
                error=error,
                status="unhealthy",
                services=services_status or {},
                **kwargs
            )