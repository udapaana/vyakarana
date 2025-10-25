#!/usr/bin/env python3
"""Load environment variables from .env file.

Provides a simple utility to load API keys from .env file.
"""

import os
from pathlib import Path


def load_env():
    """Load environment variables from .env file if it exists.

    Why this helper: Centralizes env loading logic, easier to debug if issues.
    """
    try:
        from dotenv import load_dotenv
    except ImportError:
        print("Warning: python-dotenv not installed")
        print("Install with: pip install python-dotenv")
        return False

    # Find .env file in project root
    env_path = Path(__file__).parent.parent / ".env"

    if not env_path.exists():
        print(f"Warning: {env_path} not found")
        print("Copy .env.template to .env and add your API keys")
        return False

    # Load environment variables
    load_dotenv(env_path)

    return True


def check_api_keys():
    """Check if required API keys are set.

    Returns:
        Dict with status of each API key
    """
    status = {}

    # Check Anthropic API key (from .env or system environment)
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    status['anthropic'] = {
        'set': bool(anthropic_key and anthropic_key != 'your-anthropic-api-key-here' and anthropic_key != ''),
        'value': anthropic_key[:10] + '...' if anthropic_key and len(anthropic_key) > 10 else None,
        'source': 'system' if anthropic_key and anthropic_key != '' else 'not set'
    }

    # Check Google credentials (can be API key or path to JSON)
    google_creds = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if google_creds and google_creds not in ['', '/path/to/google-vision-credentials.json']:
        # Check if it's a file path or an API key
        if google_creds.startswith('AIza'):  # Google API keys start with AIza
            status['google'] = {
                'set': True,
                'type': 'api_key',
                'value': google_creds[:10] + '...'
            }
        else:
            # Assume it's a file path
            creds_path = Path(google_creds)
            status['google'] = {
                'set': creds_path.exists(),
                'type': 'json_file',
                'path': str(creds_path),
                'exists': creds_path.exists()
            }
    else:
        status['google'] = {
            'set': False,
            'type': None,
            'value': None
        }

    return status


def main():
    """Test loading environment variables."""
    print("="*70)
    print("Environment Setup Check")
    print("="*70)
    print()

    # Load .env
    loaded = load_env()
    if loaded:
        print("✓ .env file loaded")
    else:
        print("✗ .env file not loaded")

    print()

    # Check API keys
    status = check_api_keys()

    print("API Key Status:")
    print()

    # Anthropic
    if status['anthropic']['set']:
        print(f"✓ ANTHROPIC_API_KEY: {status['anthropic']['value']}")
    else:
        print("✗ ANTHROPIC_API_KEY: Not set")
        print("  Get key from: https://console.anthropic.com/")

    print()

    # Google
    if status['google']['set']:
        if status['google']['type'] == 'api_key':
            print(f"✓ GOOGLE_APPLICATION_CREDENTIALS: {status['google']['value']} (API key)")
        else:
            print(f"✓ GOOGLE_APPLICATION_CREDENTIALS: {status['google']['path']} (JSON file)")
    else:
        print("✗ GOOGLE_APPLICATION_CREDENTIALS: Not set")
        print("  Setup: https://console.cloud.google.com/")

    print()
    print("="*70)

    if status['anthropic']['set'] and status['google']['set']:
        print("✓ All API keys configured!")
        print("\nReady to run OCR pipeline")
    else:
        print("⚠ Missing API keys")
        print("\nEdit .env file and add your credentials")


if __name__ == "__main__":
    main()
