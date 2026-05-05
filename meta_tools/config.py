import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY: str = os.environ.get("ANTHROPIC_API_KEY", "")
ANALYZER_MODEL: str = os.environ.get("ANALYZER_MODEL", "claude-sonnet-4-6")
CONFIDENCE_THRESHOLD: float = float(os.environ.get("CONFIDENCE_THRESHOLD", "0.85"))
MAX_TOKENS: int = int(os.environ.get("MAX_TOKENS", "2048"))
