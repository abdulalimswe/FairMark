import os

CANVAS_BASE_URL = os.getenv("CANVAS_BASE_URL", "").rstrip("/")
CANVAS_TOKEN = os.getenv("CANVAS_TOKEN", "")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

POLICY_TEXT = os.getenv("FAIRMARK_POLICY_TEXT", "").strip()
POLICY_FILE_PATH = os.getenv("FAIRMARK_POLICY_FILE", "").strip()

LATE_RULES_JSON = os.getenv("FAIRMARK_LATE_RULES_JSON", "").strip()

REQUEST_TIMEOUT = int(os.getenv("FAIRMARK_TIMEOUT_SEC", "30"))
