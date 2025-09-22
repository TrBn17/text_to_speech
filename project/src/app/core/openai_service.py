from typing import Dict, Any, Optional
import os
import base64
from datetime import datetime
from ..config.settings import settings
from src.app.utils.file_handler import file_handler

# Optional OpenAI import
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None

class OpenAIService:
    def __init__(self, api_key: Optional[str] = None):
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not installed. Install with: pip install openai")

        # Try to get API key from: parameter > settings > environment
        self.api_key = (
            api_key or 
            getattr(settings.openai, 'api_key', None) or 
            os.getenv("OPENAI_API_KEY") or 
            os.getenv("OPENAI__API_KEY")
        )
        if not self.api_key:
            raise ValueError("OpenAI API key is required")

        self.client = OpenAI(api_key=self.api_key)

    async def generate_text_with_files(self, prompt: str, files: list = None, model: str = "gpt-4o-mini",
                                     system_prompt: str = "", temperature: float = 0.7,
                                     top_p: float = 0.9, max_tokens: int = 100) -> Dict[str, Any]:
        """Generate text with file attachments using OpenAI file upload and vision APIs"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            # Start with text prompt
            user_content = [{"type": "text", "text": prompt}]

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
                        if mime_type.startswith('image/'):
                            # For images, use Vision API with base64 encoding
                            with open(file_path, 'rb') as f:
                                image_data = f.read()

                            base64_image = base64.b64encode(image_data).decode('utf-8')
                            user_content.append({
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{base64_image}",
                                    "detail": "high"
                                }
                            })
                        elif mime_type == 'application/pdf':
                            # PDFs are now supported directly (as of 2025)
                            with open(file_path, 'rb') as f:
                                pdf_data = f.read()

                            base64_pdf = base64.b64encode(pdf_data).decode('utf-8')
                            user_content.append({
                                "type": "image_url",  # PDFs use same structure as images
                                "image_url": {
                                    "url": f"data:application/pdf;base64,{base64_pdf}",
                                    "detail": "high"
                                }
                            })
                        else:
                            # For documents, read content and include as text preview
                            # OpenAI Chat Completions doesn't support file uploads - only Assistants API does
                            try:
                                with open(file_path, 'rb') as f:
                                    file_data = f.read()

                                # Try to decode text content for analysis
                                if mime_type.startswith('text/') or mime_type in ['application/json', 'text/csv']:
                                    try:
                                        text_content = file_data.decode('utf-8')[:8000]  # Limit to 8K chars
                                        user_content.append({
                                            "type": "text",
                                            "text": f"\n\n--- File: {filename} ({mime_type}) ---\n{text_content}"
                                        })
                                    except UnicodeDecodeError:
                                        user_content.append({
                                            "type": "text",
                                            "text": f"\n\n--- File: {filename} ({mime_type}) ---\n[Binary file - cannot display content. Please describe what you'd like me to analyze about this {mime_type} file.]"
                                        })
                                elif mime_type in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
                                    # DOCX files - not supported directly
                                    user_content.append({
                                        "type": "text",
                                        "text": f"\n\n--- File: {filename} (DOCX Document) ---\nThis is a Microsoft Word document. Size: {len(file_data)} bytes.\n\n⚠️ Note: OpenAI Chat API does not support DOCX files directly. Please:\n1. Convert to PDF format, or\n2. Copy and paste the text content directly\n\nWhat would you like me to help you with regarding this document?"
                                    })
                                else:
                                    # For other binary formats, provide file info
                                    user_content.append({
                                        "type": "text",
                                        "text": f"\n\n--- File: {filename} ({mime_type}) ---\nThis is a {mime_type} document. Size: {len(file_data)} bytes. Note: OpenAI Chat API has limited support for binary documents. Supported formats: Images (JPG, PNG, etc.) and PDFs. Please describe what you'd like me to help you with regarding this file."
                                    })
                            except Exception as read_error:
                                user_content.append({
                                    "type": "text",
                                    "text": f"\n\n--- File: {filename} ---\nError reading file: {str(read_error)}"
                                })
                    
                    except Exception as file_error:
                        print(f"Error processing file {filename}: {file_error}")
                        user_content.append({
                            "type": "text",
                            "text": f"\n\n--- File: {filename} ---\nError processing this file: {str(file_error)}"
                        })

            messages.append({"role": "user", "content": user_content})

            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p
            )

            return {
                "success": True,
                "generated_text": response.choices[0].message.content,
                "model": model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
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
    async def generate_text(self, prompt: str, model: str = "gpt-4o-mini",
                           system_prompt: str = "", temperature: float = 0.7,
                           top_p: float = 0.9, max_tokens: int = 100) -> Dict[str, Any]:
        """Generate text using OpenAI models"""
        return await self.generate_text_with_files(
            prompt=prompt, files=None, model=model, system_prompt=system_prompt,
            temperature=temperature, top_p=top_p, max_tokens=max_tokens
        )

    async def generate_text_stream(self, prompt: str, model: str = "gpt-3.5-turbo",
                                  system_prompt: str = "", temperature: float = 0.7,
                                  top_p: float = 0.9, max_tokens: int = 100) -> Dict[str, Any]:
        """Generate text using OpenAI models with streaming"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            stream = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stream=True
            )

            async def stream_generator():
                """Generator function for streaming chunks"""
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        yield chunk.choices[0].delta.content

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

    async def text_to_speech(self, text: str, voice: str = "alloy",
                            model: str = "tts-1", speed: float = 1.0,
                            instructions: str = "", response_format: str = "mp3") -> Dict[str, Any]:
        """Convert text to speech using OpenAI TTS"""
        try:
            # Prepare request parameters
            request_params = {
                "model": model,
                "voice": voice,
                "input": text,
                "speed": speed,
                "response_format": response_format
            }
            
            # Add instructions if provided and model supports it
            # Instructions don't work with tts-1 or tts-1-hd according to docs
            if instructions and model not in ["tts-1", "tts-1-hd"]:
                request_params["instructions"] = instructions

            response = self.client.audio.speech.create(**request_params)

            # Convert audio to base64 for easy transport
            audio_data = response.content
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')

            # Calculate approximate duration (rough estimate)
            duration = len(text) * 0.08  # ~80ms per character

            return {
                "success": True,
                "audio_base64": audio_base64,
                "audio_format": response_format,
                "text": text,
                "voice": voice,
                "model": model,
                "speed": speed,
                "instructions": instructions if instructions else "",
                "duration": duration,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "text": text,
                "voice": voice,
                "model": model,
                "timestamp": datetime.now().isoformat()
            }

    def get_available_models(self) -> Dict[str, Any]:
        """Get available OpenAI models"""
        return {
            "text_generation": [
                "gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"
            ],
            "text_to_speech": ["tts-1", "tts-1-hd"],
            "voices": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        }