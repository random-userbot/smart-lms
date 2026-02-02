"""
Config loader for API keys
Reads from config.yaml or environment variables
"""

import os
import yaml
from pathlib import Path


def load_config():
    """Load configuration from config.yaml"""
    config_path = Path(__file__).parent.parent / "config.yaml"
    
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Warning: Could not load config.yaml: {e}")
            return {}
    return {}


def get_api_key(provider: str) -> str:
    """
    Get API key for provider from config.yaml or environment variable
    
    Args:
        provider: 'groq', 'openai', or 'gemini'
    
    Returns:
        API key string or None
    """
    # Map provider names to config keys and env var names
    key_mapping = {
        'groq': ('groq_api_key', 'GROQ_API_KEY'),
        'openai': ('openai_api_key', 'OPENAI_API_KEY'),
        'gemini': ('google_api_key', 'GOOGLE_API_KEY')
    }
    
    if provider not in key_mapping:
        return None
    
    config_key, env_var = key_mapping[provider]
    
    # Try config.yaml first
    config = load_config()
    api_key = config.get(config_key)
    
    if api_key:
        return api_key
    
    # Fall back to environment variable
    return os.getenv(env_var)


if __name__ == "__main__":
    # Test
    print("Testing API key configuration...")
    print(f"Groq API key: {'✓ Found' if get_api_key('groq') else '✗ Not found'}")
    print(f"OpenAI API key: {'✓ Found' if get_api_key('openai') else '✗ Not found'}")
    print(f"Gemini API key: {'✓ Found' if get_api_key('gemini') else '✗ Not found'}")
