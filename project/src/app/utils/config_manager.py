"""
Configuration Manager - Single responsibility: Load and manage configuration files
Consolidates 6 duplicate config loading implementations
"""
import json
import os
from typing import Dict, Any, Optional


class ConfigManager:
    """Single source of truth for all configuration loading"""

    @staticmethod
    def load_models_config() -> Dict[str, Any]:
        """Load models configuration from models.json file"""
        try:
            config_path = os.path.join(
                os.path.dirname(__file__), "..", "config", "models.json"
            )
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: models.json not found at {config_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"Warning: Invalid JSON in models.json: {e}")
            return {}
        except Exception as e:
            print(f"Warning: Could not load models config: {e}")
            return {}

    @staticmethod
    def get_system_prompts(category: str = "default") -> Dict[str, str]:
        """Get system prompts by category"""
        config = ConfigManager.load_models_config()
        return config.get("system_prompts", {}).get(category, {})

    @staticmethod
    def get_models_by_provider(provider: str, model_type: str = "text_generation") -> Dict[str, Any]:
        """Get models for specific provider and type"""
        config = ConfigManager.load_models_config()
        return config.get(model_type, {}).get(provider, {})

    @staticmethod
    def get_voices_config() -> Dict[str, Any]:
        """Get voices configuration"""
        config = ConfigManager.load_models_config()
        return config.get("voices", {})

    @staticmethod
    def get_tts_models_by_provider(provider: str) -> Dict[str, Any]:
        """Get TTS models for specific provider"""
        return ConfigManager.get_models_by_provider(provider, "text_to_speech")

    @staticmethod
    def get_config_path() -> str:
        """Get the path to models.json file"""
        return os.path.join(
            os.path.dirname(__file__), "..", "config", "models.json"
        )

    @staticmethod
    def is_config_valid() -> bool:
        """Check if configuration file exists and is valid JSON"""
        try:
            ConfigManager.load_models_config()
            return True
        except Exception:
            return False