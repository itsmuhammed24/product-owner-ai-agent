"""Config env — GROQ, Canny, limites (MAX_FEEDBACKS, MAX_TEXT_LENGTH)."""

from __future__ import annotations

import os

from pydantic import BaseModel

# Limites par défaut (sécurité / coût)
MAX_FEEDBACKS_DEFAULT = 100
MAX_TEXT_LENGTH_DEFAULT = 10_000
MAX_INGEST_SIZE_MB_DEFAULT = 5.0
MAX_INGEST_SIZE_MB_MIN = 0.1
MAX_INGEST_SIZE_MB_MAX = 50.0
MAX_CHAT_MESSAGE_LENGTH = 4000

# Groq — provider LLM par défaut (gratuit, rapide)
GROQ_MODEL_DEFAULT = "llama-3.1-8b-instant"

_settings_cache: "Settings | None" = None


class Settings(BaseModel):
    groq_api_key: str = ""
    groq_model: str = GROQ_MODEL_DEFAULT
    canny_api_key: str = ""
    canny_board_id: str = ""
    product_name: str = ""
    target_segment: str = ""
    max_feedbacks: int = MAX_FEEDBACKS_DEFAULT
    max_text_length: int = MAX_TEXT_LENGTH_DEFAULT
    max_ingest_size_mb: float = MAX_INGEST_SIZE_MB_DEFAULT
    max_chat_message_length: int = MAX_CHAT_MESSAGE_LENGTH

    model_config = {"extra": "ignore"}


def get_settings() -> Settings:
    global _settings_cache
    if _settings_cache is not None:
        return _settings_cache
    raw_mb = float(os.getenv("MAX_INGEST_SIZE_MB", str(MAX_INGEST_SIZE_MB_DEFAULT)))
    max_ingest = max(MAX_INGEST_SIZE_MB_MIN, min(MAX_INGEST_SIZE_MB_MAX, raw_mb))
    _settings_cache = Settings(
        groq_api_key=os.getenv("GROQ_API_KEY", "").strip(),
        groq_model=os.getenv("GROQ_MODEL", GROQ_MODEL_DEFAULT).strip(),
        canny_api_key=os.getenv("CANNY_API_KEY", "").strip(),
        canny_board_id=os.getenv("CANNY_BOARD_ID", "").strip(),
        product_name=os.getenv("PRODUCT_NAME", "").strip(),
        target_segment=os.getenv("TARGET_SEGMENT", "").strip(),
        max_feedbacks=int(os.getenv("MAX_FEEDBACKS", str(MAX_FEEDBACKS_DEFAULT))),
        max_text_length=int(os.getenv("MAX_TEXT_LENGTH", str(MAX_TEXT_LENGTH_DEFAULT))),
        max_ingest_size_mb=max_ingest,
        max_chat_message_length=int(
            os.getenv("MAX_CHAT_MESSAGE_LENGTH", str(MAX_CHAT_MESSAGE_LENGTH))
        ),
    )
    return _settings_cache
