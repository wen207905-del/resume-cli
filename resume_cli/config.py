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
    timeout: float = 60.0
    max_resume_chars: int = 15000
    json_mode: bool = True


def get_settings() -> Settings:
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY", "").strip(),
        openai_base_url=os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com").strip(),
        openai_model=os.getenv("OPENAI_MODEL", "deepseek-chat").strip(),
        max_retries=int(os.getenv("OPENAI_MAX_RETRIES", "2")),
        temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.1")),
        timeout=float(os.getenv("API_TIMEOUT", "60")),
        max_resume_chars=int(os.getenv("MAX_RESUME_CHARS", "15000")),
        json_mode=os.getenv("JSON_MODE", "true").lower() in ("1", "true", "yes"),
    )


def ensure_api_key(settings: Settings, mock: bool) -> None:
    if mock:
        return
    key = settings.openai_api_key
    if not key or key.startswith("sk-your-"):
        raise ValueError(
            "未配置有效的 OPENAI_API_KEY。\n"
            "请复制 .env.example 为 .env，填入 DeepSeek Key：\n"
            "  https://platform.deepseek.com/api_keys\n"
            "或使用 --mock 模式本地演示。"
        )


def resolve_path(path: str | Path) -> Path:
    resolved = Path(path).expanduser().resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"文件不存在: {resolved}")
    return resolved
