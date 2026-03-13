"""
NexCall AI — Configuration centralisée
Toutes les variables sont chargées depuis .env via pydantic-settings.
"""
from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration principale de l'application NexCall AI."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Application ───────────────────────────────────────────────
    APP_NAME: str = "NexCall AI"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = False
    SECRET_KEY: str = "nexcall-dev-secret-key-change-in-production"
    CORS_ORIGINS: List[str] = ["*"]

    # ── Base de données ───────────────────────────────────────────
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/nexcall.db"

    # ── Ringover ──────────────────────────────────────────────────
    RINGOVER_API_KEY: Optional[str] = None
    RINGOVER_API_URL: str = "https://public-api.ringover.com/v2"
    RINGOVER_WEBHOOK_SECRET: Optional[str] = None
    RINGOVER_PHONE_NUMBER: Optional[str] = None
    RINGOVER_TRANSFER_NUMBER: Optional[str] = None

    # ── OpenAI ────────────────────────────────────────────────────
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_TTS_MODEL: str = "tts-1"
    OPENAI_TTS_VOICE: str = "nova"
    OPENAI_STT_MODEL: str = "whisper-1"
    OPENAI_MAX_TOKENS: int = 600

    # ── Agent IA ──────────────────────────────────────────────────
    AI_AGENT_NAME: str = "Sophie"
    AI_COMPANY_NAME: str = "AssurancePro"
    AI_LANGUAGE: str = "fr"
    AI_TEMPERATURE: float = 0.7

    # ── IVR ───────────────────────────────────────────────────────
    IVR_GREETING: str = (
        "Bonjour et bienvenue. "
        "Pour l'assurance auto, tapez 1. "
        "Pour l'assurance santé, tapez 2. "
        "Pour parler à un conseiller, tapez 3."
    )

    # ── Leads ─────────────────────────────────────────────────────
    LEAD_SCORE_THRESHOLD: int = 70

    # ── Propriétés calculées ──────────────────────────────────────
    @property
    def is_ringover_configured(self) -> bool:
        """Vérifie si Ringover est configuré."""
        return bool(self.RINGOVER_API_KEY and self.RINGOVER_API_KEY != "votre_cle_api_ringover")

    @property
    def is_openai_configured(self) -> bool:
        """Vérifie si OpenAI est configuré."""
        return bool(self.OPENAI_API_KEY and self.OPENAI_API_KEY != "sk-votre_cle_openai")


@lru_cache()
def get_settings() -> Settings:
    """Retourne l'instance singleton des settings."""
    return Settings()


settings = get_settings()
