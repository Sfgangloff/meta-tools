import os

ANALYZER_MODEL: str = os.environ.get("ANALYZER_MODEL", "claude-sonnet-4-6")
CONFIDENCE_THRESHOLD: float = float(os.environ.get("CONFIDENCE_THRESHOLD", "0.85"))
