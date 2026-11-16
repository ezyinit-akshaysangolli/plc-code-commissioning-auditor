import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# Check Google's current model list and override in .env if these are retired
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash") # or "gemini-3.5-turbo" for a more capable model
EMBED_MODEL = os.getenv("GEMINI_EMBED_MODEL", "gemini-embedding-001")


def get_api_key() -> str:
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not key:
        raise ValueError("No API key found. Add GEMINI_API_KEY=... to the .env file in the project root.")
    return key