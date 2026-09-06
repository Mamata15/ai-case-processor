"""Application configuration loaded from environment variables."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


def _path_from_env(name: str, default: str) -> Path:
    configured_path = Path(os.getenv(name, default))
    return configured_path if configured_path.is_absolute() else PROJECT_ROOT / configured_path


@dataclass(frozen=True)
class Settings:
    """Runtime settings for the batch processor."""

    llm_provider: str = os.getenv("LLM_PROVIDER", "openai")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
    data_dir: Path = _path_from_env("DATA_DIR", "data")
    output_dir: Path = _path_from_env("OUTPUT_DIR", "output")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    send_emails: bool = os.getenv("SEND_EMAILS", "false").lower() == "true"
    smtp_host: str = os.getenv("SMTP_HOST", "")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: Optional[str] = os.getenv("SMTP_USERNAME")
    smtp_password: Optional[str] = os.getenv("SMTP_PASSWORD")
    sender_email: Optional[str] = os.getenv("SENDER_EMAIL")
    smtp_use_tls: bool = os.getenv("SMTP_USE_TLS", "true").lower() == "true"


settings = Settings()