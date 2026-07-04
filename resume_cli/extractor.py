"""Structured resume extraction from raw text."""

from __future__ import annotations

from resume_cli.ai_client import AIClient
from resume_cli.config import Settings
from resume_cli.mock_data import MOCK_RESUME
from resume_cli.prompts import EXTRACT_SYSTEM, EXTRACT_USER
from resume_cli.schemas import ResumeData


def trim_resume_text(text: str, max_chars: int) -> str:
    text = text.strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[简历过长，已截断]"


def extract_resume(
    resume_text: str,
    client: AIClient,
    settings: Settings | None = None,
) -> ResumeData:
    if client.mock:
        return MOCK_RESUME.model_copy(deep=True)

    limit = settings.max_resume_chars if settings else client.settings.max_resume_chars
    trimmed = trim_resume_text(resume_text, limit)
    user_prompt = EXTRACT_USER.format(resume_text=trimmed)
    return client.parse_structured(
        ResumeData,
        EXTRACT_SYSTEM,
        user_prompt,
        schema_hint=ResumeData.model_json_schema(),
    )
