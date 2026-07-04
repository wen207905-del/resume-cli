"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    openai_base_url: str
    openai_model: str
    max_retries: int = 2
    temperature: float = 0.1


def get_settings() -> Settings:
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        max_retries=int(os.getenv("OPENAI_MAX_RETRIES", "2")),
        temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.1")),
    )


def ensure_api_key(settings: Settings, mock: bool) -> None:
    if mock:
        return
    if not settings.openai_api_key:
        raise ValueError(
            "未配置 OPENAI_API_KEY。请在 .env 中设置，或使用 --mock 模式运行。"
        )


def resolve_path(path: str | Path) -> Path:
    resolved = Path(path).expanduser().resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"文件不存在: {resolved}")
    return resolved
