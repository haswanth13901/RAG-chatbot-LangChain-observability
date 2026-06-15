import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY   = os.getenv("GROQ_API_KEY")
APP_API_KEY    = os.getenv("APP_API_KEY")

GROQ_CHAT_MODEL   = "llama-3.1-8b-instant"
GEMINI_CHAT_MODEL = "gemini-2.0-flash"
EMBED_MODEL       = "gemini-embedding-2-preview"

MEMORY_WINDOW        = 10
RETRIEVAL_K          = 4
SIMILARITY_THRESHOLD = 0.3
MIN_RELEVANT_CHUNKS  = 1
RERANK_TOP_N         = 3

RATE_LIMIT_REQUESTS       = 20
RATE_LIMIT_WINDOW_SECONDS = 60

BASE_DIR   = Path(__file__).parent.parent
DOCS_DIR   = next(
    (BASE_DIR / name for name in ("docs", "Docs") if (BASE_DIR / name).exists()),
    BASE_DIR / "Docs",
)
CHROMA_DIR = BASE_DIR / "chroma_db"

def validate_config() -> list[str]:
    warnings = []
    if not GOOGLE_API_KEY:
        warnings.append("GOOGLE_API_KEY is not set — embeddings will fail")
    if not GROQ_API_KEY:
        warnings.append("GROQ_API_KEY is not set — will fall back to Gemini for chat")
    if not APP_API_KEY:
        warnings.append("APP_API_KEY is not set — all endpoints are unprotected")
    return warnings

REWARD_RULES: dict[str, dict] = {
    "purchase": {
        "base_points_per_dollar": 10,
        "description": "Standard retail or online purchase",
        "bonus_categories": {
            "groceries":   {"multiplier": 2.0, "label": "2x on groceries"},
            "dining":      {"multiplier": 3.0, "label": "3x on dining"},
            "travel":      {"multiplier": 5.0, "label": "5x on travel bookings"},
            "electronics": {"multiplier": 1.5, "label": "1.5x on electronics"},
        },
        "min_amount": 1.00,
    },
    "transfer": {
        "base_points_per_dollar": 2,
        "description": "Bank or wallet transfer",
        "bonus_categories": {},
        "min_amount": 10.00,
    },
    "bill_payment": {
        "base_points_per_dollar": 5,
        "description": "Utility, insurance, or subscription bill payment",
        "bonus_categories": {
            "utilities": {"multiplier": 1.5, "label": "1.5x on utilities"},
            "insurance": {"multiplier": 2.0, "label": "2x on insurance"},
        },
        "min_amount": 5.00,
    },
    "referral": {
        "flat_points": 500,
        "description": "New user referral bonus",
        "bonus_categories": {},
        "min_amount": 0,
    },
    "subscription": {
        "base_points_per_dollar": 8,
        "description": "Recurring subscription payment",
        "bonus_categories": {
            "streaming": {"multiplier": 2.0, "label": "2x on streaming"},
        },
        "min_amount": 1.00,
    },
}