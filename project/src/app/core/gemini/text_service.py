"""
Gemini Text Service - Single responsibility: Handle text generation only
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

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

from .file_uploader import GeminiFileUploader


class GeminiTextService:
    """Handles text generation for Gemini - only text generation logic"""

    def __init__(self, client: Optional[object] = None, legacy_mode: bool = False):
        self.client = client
        self.legacy_mode = legacy_mode
        self.file_uploader = GeminiFileUploader(client, legacy_mode)

    async def generate_text_only(self, prompt: str, model: str = "gemini-2.0-flash",
                                system_prompt: str = "", temperature: float = 0.7,
                                max_tokens: int = 100) -> Dict[str, Any]:
        """Generate text without files - simple text generation"""
        try:
            if self.legacy_mode:
                return await self._generate_legacy_text_only(
                    prompt, model, system_prompt, temperature, max_tokens)
            else:
                return await self._generate_new_text_only(
                    prompt, model, system_prompt, temperature, max_tokens)

        except Exception as e:
            return self._create_error_response(str(e), model)

    async def generate_text_with_files(self, prompt: str, files: List[Dict[str, Any]],
                                     model: str = "gemini-2.0-flash", system_prompt: str = "",
                                     temperature: float = 0.7, max_tokens: int = 100) -> Dict[str, Any]:
        """Generate text with file attachments"""
        try:
            if self.legacy_mode:
                return await self._generate_legacy_with_files(
                    prompt, files, model, system_prompt, temperature, max_tokens)
            else:
                return await self._generate_new_with_files(
                    prompt, files, model, system_prompt, temperature, max_tokens)

        except Exception as e:
            return self._create_error_response(str(e), model)

    async def _generate_new_text_only(self, prompt: str, model: str, system_prompt: str,
                                    temperature: float, max_tokens: int) -> Dict[str, Any]:
        """Generate text using new SDK without files"""
        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

        if system_prompt:
            config.system_instruction = system_prompt

        response = self.client.models.generate_content(
            model=model,
            contents=[prompt],
            config=config
        )

        return self._create_success_response(response, model)

    async def _generate_new_with_files(self, prompt: str, files: List[Dict[str, Any]],
                                     model: str, system_prompt: str, temperature: float,
                                     max_tokens: int) -> Dict[str, Any]:
        """Generate text using new SDK with files"""
        contents = [prompt]

        # Process files and add to contents
        for file_info in files:
            file_path = file_info.get('file_path')
            mime_type = file_info.get('mime_type', '')
            filename = file_info.get('filename', '')

            if not file_path:
                contents.append(f"Error: File path missing for {filename}")
                continue

            # Decide upload method
            upload_method = self.file_uploader.decide_upload_method(file_path, mime_type)

            if upload_method == "inline":
                # Use inline for small files
                result = self.file_uploader.create_inline_part(file_path, mime_type)
                if result["success"]:
                    contents.append(result["part"])
                    contents.append(f"Analyze this file: {filename}")
                else:
                    contents.append(f"Error processing {filename}: {result['error']}")
            else:
                # Use file API for large files
                result = self.file_uploader.upload_file(file_path, mime_type)
                if result["success"]:
                    contents.append(result["file"])
                    contents.append(f"Analyze this document: {filename}")
                else:
                    contents.append(f"Error uploading {filename}: {result['error']}")

        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

        if system_prompt:
            config.system_instruction = system_prompt

        response = self.client.models.generate_content(
            model=model,
            contents=contents,
            config=config
        )

        return self._create_success_response(response, model)

    async def _generate_legacy_text_only(self, prompt: str, model: str, system_prompt: str,
                                       temperature: float, max_tokens: int) -> Dict[str, Any]:
        """Generate text using legacy SDK without files"""
        generation_config = genai.types.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
        )

        model_instance = genai.GenerativeModel(
            model_name=model,
            generation_config=generation_config,
            system_instruction=system_prompt if system_prompt else None
        )

        response = model_instance.generate_content([prompt])
        return self._create_success_response(response, model)

    async def _generate_legacy_with_files(self, prompt: str, files: List[Dict[str, Any]],
                                        model: str, system_prompt: str, temperature: float,
                                        max_tokens: int) -> Dict[str, Any]:
        """Generate text using legacy SDK with files"""
        content_parts = [prompt]

        # Process files for legacy mode
        for file_info in files:
            file_path = file_info.get('file_path')
            filename = file_info.get('filename', '')

            if not file_path:
                content_parts.append(f"Error: File path missing for {filename}")
                continue

            result = self.file_uploader.upload_file(file_path, "")  # Legacy doesn't need mime_type
            if result["success"]:
                content_parts.append(result["file"])
                content_parts.append(f"Analyze this file: {filename}")
            else:
                content_parts.append(f"Error uploading {filename}: {result['error']}")

        generation_config = genai.types.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
        )

        model_instance = genai.GenerativeModel(
            model_name=model,
            generation_config=generation_config,
            system_instruction=system_prompt if system_prompt else None
        )

        response = model_instance.generate_content(content_parts)
        return self._create_success_response(response, model)

    def _create_success_response(self, response: object, model: str) -> Dict[str, Any]:
        """Create standardized success response"""
        # Extract usage data if available
        usage_data = {}
        if hasattr(response, 'usage_metadata'):
            try:
                usage_metadata = response.usage_metadata
                usage_data = {
                    "prompt_tokens": getattr(usage_metadata, 'prompt_token_count', 0),
                    "completion_tokens": getattr(usage_metadata, 'candidates_token_count', 0),
                    "total_tokens": getattr(usage_metadata, 'total_token_count', 0)
                }
            except Exception:
                usage_data = {}

        return {
            "success": True,
            "generated_text": response.text,
            "model": model,
            "usage": usage_data,
            "timestamp": datetime.now().isoformat()
        }

    def _create_error_response(self, error: str, model: str) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            "success": False,
            "error": error,
            "generated_text": f"Error generating text: {error}",
            "model": model,
            "timestamp": datetime.now().isoformat()
        }