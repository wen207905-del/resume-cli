"""Shared resume processing logic for CLI and Web."""

from __future__ import annotations

import tempfile
from pathlib import Path

from resume_cli.ai_client import AIClient
from resume_cli.config import Settings
from resume_cli.extractor import extract_resume
from resume_cli.pdf_parser import extract_text_from_pdf
from resume_cli.schemas import ExtractResult, ResumeData, ScoreResult
from resume_cli.scorer import score_resume


def parse_pdf_bytes(content: bytes) -> str:
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)
    try:
        return extract_text_from_pdf(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)


def run_extract(content: bytes, settings: Settings, mock: bool = False) -> ResumeData:
    text = parse_pdf_bytes(content)
    client = AIClient(settings, mock=mock)
    return extract_resume(text, client, settings)


def run_score(
    content: bytes,
    jd_text: str,
    settings: Settings,
    mock: bool = False,
) -> ExtractResult:
    text = parse_pdf_bytes(content)
    client = AIClient(settings, mock=mock)
    resume = extract_resume(text, client, settings)
    score = score_resume(resume, jd_text.strip(), client)
    return ExtractResult(resume=resume, score=score)
