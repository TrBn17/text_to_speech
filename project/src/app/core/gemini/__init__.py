"""
Gemini services module - Focused, single-responsibility components
"""

from .client_factory import GeminiClientFactory
from .file_uploader import GeminiFileUploader
from .text_service import GeminiTextService
from .tts_service import GeminiTTSService
from .google_tts_service import GoogleCloudTTSService

__all__ = [
    'GeminiClientFactory',
    'GeminiFileUploader', 
    'GeminiTextService',
    'GeminiTTSService',
    'GoogleCloudTTSService'
]

# Multiple images upload functionality is now available:
# - GeminiFileUploader.upload_multiple_files()
# - GeminiFileUploader.create_multiple_inline_parts() 
# - GeminiFileUploader.batch_upload_with_method_selection()
# - GeminiFileUploader.validate_image_files()
# - GeminiTextService.generate_text_with_multiple_images()
#
# See example_multiple_images.py for usage examples