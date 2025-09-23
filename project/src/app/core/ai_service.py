from typing import Dict, Any, Optional, List
import os
import base64
from datetime import datetime
from ..config.settings import settings
from .openai_tts_service import OpenAITTSService

# Gemini import
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

class AIService:
    def __init__(self, api_key: Optional[str] = None):
        if not GEMINI_AVAILABLE:
            raise ImportError("Google Generative AI library not installed. Install with: pip install google-generativeai")

        # Try to get Gemini API key from: parameter > settings > environment
        self.api_key = (
            api_key or
            getattr(settings.gemini, 'api_key', None) or
            os.getenv("GEMINI_API_KEY") or
            os.getenv("GEMINI__API_KEY")
        )
        if not self.api_key:
            raise ValueError("Gemini API key is required")

        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

        # Initialize OpenAI TTS service if API key is available
        self.openai_tts_service = None
        try:
            openai_key = getattr(settings.openai, 'api_key', None) or os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI__API_KEY")
            if openai_key:
                self.openai_tts_service = OpenAITTSService(openai_key)
        except Exception:
            pass

    async def generate_text_with_files(self, prompt: str, files: list = None, model: str = "gemini-2.0-flash-exp",
                                     system_prompt: str = "", temperature: float = 0.7,
                                     top_p: float = 0.9, max_tokens: int = 100) -> Dict[str, Any]:
        """Generate text with file attachments using Gemini document processing"""
        try:
            # Prepare content for Gemini
            content_parts = []

            # Add system prompt if provided
            if system_prompt:
                content_parts.append(f"System: {system_prompt}\n\n")

            # Process files if provided
            if files:
                for file_info in files:
                    file_path = file_info.get('file_path')
                    mime_type = file_info.get('mime_type', '')
                    filename = file_info.get('filename', '')

                    if not file_path or not os.path.exists(file_path):
                        print(f"Warning: File path not found for {filename}")
                        continue

                    try:
                        if mime_type == 'application/pdf':
                            # Handle PDF using Gemini's document processing
                            with open(file_path, 'rb') as f:
                                pdf_data = f.read()

                            # Check file size (max 50MB for Gemini File API)
                            if len(pdf_data) > 50 * 1024 * 1024:
                                content_parts.append(f"\n\n--- File: {filename} ---\nPDF file too large (>50MB). Please use a smaller file.")
                                continue

                            # For files under 20MB, use inline data
                            if len(pdf_data) <= 20 * 1024 * 1024:
                                # Upload inline PDF data
                                pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
                                content_parts.append({
                                    "inline_data": {
                                        "mime_type": "application/pdf",
                                        "data": pdf_base64
                                    }
                                })
                            else:
                                # Use File API for larger files
                                uploaded_file = genai.upload_file(file_path, mime_type=mime_type)
                                content_parts.append(uploaded_file)

                        elif mime_type.startswith('image/') and mime_type in ['image/jpeg', 'image/png', 'image/gif', 'image/webp']:
                            # Handle images
                            with open(file_path, 'rb') as f:
                                image_data = f.read()

                            # Check file size (max 20MB for inline)
                            if len(image_data) > 20 * 1024 * 1024:
                                content_parts.append(f"\n\n--- File: {filename} ---\nImage file too large (>20MB). Please use a smaller image.")
                                continue

                            image_base64 = base64.b64encode(image_data).decode('utf-8')
                            content_parts.append({
                                "inline_data": {
                                    "mime_type": mime_type,
                                    "data": image_base64
                                }
                            })

                        elif mime_type.startswith('text/') or mime_type in ['application/json', 'text/csv', 'text/plain']:
                            # Handle text files
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    text_content = f.read()
                                content_parts.append(f"\n\n--- File: {filename} ({mime_type}) ---\n{text_content}")
                            except Exception as e:
                                content_parts.append(f"\n\n--- File: {filename} ---\nError reading text file: {str(e)}")

                        else:
                            # For other file types, provide basic info
                            with open(file_path, 'rb') as f:
                                file_size = len(f.read())
                            content_parts.append(f"\n\n--- File: {filename} ({mime_type}) ---\nFile size: {file_size} bytes. Gemini supports PDF documents and images natively. For other file types, please convert to PDF or extract text content.")

                    except Exception as file_error:
                        print(f"Error processing file {filename}: {file_error}")
                        content_parts.append(f"\n\n--- File: {filename} ---\nError processing this file: {str(file_error)}")

            # Add user prompt
            content_parts.append(f"\n\nUser: {prompt}")

            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                top_p=top_p,
                max_output_tokens=max_tokens,
            )

            # Generate response
            response = self.model.generate_content(
                content_parts,
                generation_config=generation_config
            )

            return {
                "success": True,
                "generated_text": response.text,
                "model": model,
                "usage": {
                    "prompt_tokens": response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 0,
                    "completion_tokens": response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0,
                    "total_tokens": response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0
                },
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "generated_text": f"Error generating text: {str(e)}",
                "model": model,
                "timestamp": datetime.now().isoformat()
            }
    async def generate_text(self, prompt: str, model: str = "gemini-2.0-flash-exp",
                           system_prompt: str = "", temperature: float = 0.7,
                           top_p: float = 0.9, max_tokens: int = 100) -> Dict[str, Any]:
        """Generate text using Gemini models"""
        return await self.generate_text_with_files(
            prompt=prompt, files=None, model=model, system_prompt=system_prompt,
            temperature=temperature, top_p=top_p, max_tokens=max_tokens
        )

    async def generate_text_stream(self, prompt: str, model: str = "gemini-2.0-flash-exp",
                                  system_prompt: str = "", temperature: float = 0.7,
                                  top_p: float = 0.9, max_tokens: int = 100) -> Dict[str, Any]:
        """Generate text using Gemini models with streaming"""
        try:
            # Prepare content for Gemini
            content_parts = []

            # Add system prompt if provided
            if system_prompt:
                content_parts.append(f"System: {system_prompt}\n\n")

            # Add user prompt
            content_parts.append(f"User: {prompt}")

            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                top_p=top_p,
                max_output_tokens=max_tokens,
            )

            # Generate streaming response
            response = self.model.generate_content(
                content_parts,
                generation_config=generation_config,
                stream=True
            )

            async def stream_generator():
                """Generator function for streaming chunks"""
                for chunk in response:
                    if chunk.text:
                        yield chunk.text

            return {
                "success": True,
                "stream": stream_generator(),
                "model": model,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            async def error_generator():
                yield f"Error: {str(e)}"

            return {
                "success": False,
                "error": str(e),
                "stream": error_generator(),
                "model": model,
                "timestamp": datetime.now().isoformat()
            }

    def get_available_models(self) -> Dict[str, Any]:
        """Get available Gemini models"""
        return {
            "text_generation": [
                "gemini-2.0-flash-exp", "gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro"
            ],
            "document_processing": [
                "gemini-2.0-flash-exp", "gemini-1.5-pro", "gemini-1.5-flash"
            ],
            "supported_formats": {
                "documents": ["application/pdf"],
                "images": ["image/jpeg", "image/png", "image/gif", "image/webp"],
                "text": ["text/plain", "text/csv", "application/json"]
            },
            "limits": {
                "inline_file_size": "20MB",
                "file_api_size": "50MB",
                "pdf_pages": "1000 pages"
            }
        }

    async def text_to_speech(self, text: str, voice: str = "alloy",
                            speed: float = 1.0, provider: str = "openai",
                            model: str = None, instructions: str = "",
                            voice_config: Dict[str, Any] = None,
                            prompt_prefix: str = "",
                            response_format: str = "mp3") -> Dict[str, Any]:
        """Convert text to speech using OpenAI TTS"""

        if provider == "openai":
            if not self.openai_tts_service:
                return {"success": False, "error": "OpenAI TTS service not available"}

            tts_model = model or ("tts-1-hd" if "hd" in voice.lower() else "tts-1")
            return await self.openai_tts_service.text_to_speech(
                text=text, voice=voice, model=tts_model, speed=speed,
                instructions=instructions, response_format=response_format)
        else:
            return {"success": False, "error": f"TTS provider '{provider}' not supported"}

# Global instance
ai_service = AIService()