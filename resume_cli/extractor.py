"""Structured resume extraction from raw text."""

from __future__ import annotations

from resume_cli.ai_client import AIClient
from resume_cli.mock_data import MOCK_RESUME
from resume_cli.prompts import EXTRACT_SYSTEM, EXTRACT_USER
from resume_cli.schemas import ResumeData


def extract_resume(resume_text: str, client: AIClient) -> ResumeData:
    if client.mock:
        return MOCK_RESUME.model_copy(deep=True)

    user_prompt = EXTRACT_USER.format(resume_text=resume_text)
    return client.parse_structured(
        ResumeData,
        EXTRACT_SYSTEM,
        user_prompt,
        schema_hint=ResumeData.model_json_schema(),
    )
