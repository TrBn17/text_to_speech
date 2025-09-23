from fastapi import APIRouter, Form
from pydantic import BaseModel

router = APIRouter(prefix="/generate", tags=["Text Generation"])

class GenerateResponse(BaseModel):
    response: str

@router.post("/text")
async def generate_text(
    prompt: str = Form(..., description="Text prompt for generation"),
    max_tokens: int = Form(default=100, description="Maximum tokens to generate"),
    model: str = Form(default="gemini-2.0-flash-exp", description="Model to use"),
    system_prompt: str = Form(default="text_generation", description="System prompt type"),
    custom_system_prompt: str = Form(default="", description="Custom system prompt text"),
    temperature: float = Form(default=0.7, description="Temperature (0.0-2.0)"),
    top_p: float = Form(default=0.9, description="Top-p (0.0-1.0)")
):
    """Generate text từ prompt"""
    try:
        # Import services
        from ..core import ai_service
        from ..utils.config_manager import ConfigManager
        from ..core.cache_manager import save_api_response

        # Get system prompt text using ConfigManager
        if system_prompt == 'custom' and custom_system_prompt.strip():
            system_prompt_text = custom_system_prompt.strip()
        else:
            system_prompts = ConfigManager.get_system_prompts("default")
            system_prompt_text = system_prompts.get(system_prompt,
                "You are a helpful AI assistant. Please provide accurate and helpful responses to user queries.")

        # Generate text
        result = await ai_service.generate_text_with_files(
            prompt=prompt,
            files=[],
            model=model,
            system_prompt=system_prompt_text,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens
        )

        if result["success"]:
            generated_text = result["generated_text"]

            # 🆕 Save response to cache automatically
            try:
                cache_metadata = {
                    'original_prompt': prompt[:500],  # Store first 500 chars of prompt
                    'model': model,
                    'system_prompt': system_prompt,
                    'api_params': {
                        'max_tokens': max_tokens,
                        'temperature': temperature,
                        'top_p': top_p
                    },
                    'api_endpoint': '/api/generate/text',
                    'usage': result.get('usage', {}),
                    'timestamp': result.get('timestamp'),
                    'content_length': len(generated_text)
                }

                cache_key = save_api_response('text_generation', generated_text, cache_metadata)

                if cache_key:
                    print(f"💾 API Response cached automatically: {cache_key}")
                    print(f"   Content length: {len(generated_text)} chars")
                else:
                    print(f"⚠️ Failed to cache API response")

            except Exception as cache_error:
                print(f"⚠️ Cache error (non-critical): {cache_error}")
                # Continue even if caching fails

            return GenerateResponse(response=generated_text)
        else:
            return GenerateResponse(response=f"Error: {result.get('error', 'Unknown error')}")

    except Exception as e:
        return GenerateResponse(response=f"Error: {str(e)}")

