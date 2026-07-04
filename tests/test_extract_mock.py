"""Tests for mock extraction and scoring."""

from __future__ import annotations

import json
from pathlib import Path

import fitz
import pytest
from typer.testing import CliRunner

from resume_cli.config import Settings
from resume_cli.ai_client import AIClient
from resume_cli.extractor import extract_resume
from resume_cli.main import app
from resume_cli.scorer import score_resume

runner = CliRunner()


def _make_sample_pdf(tmp_path: Path) -> Path:
    pdf_path = tmp_path / "resume.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "张明\nPython Developer", fontsize=12, fontname="china-s")
    doc.save(pdf_path)
    doc.close()
    return pdf_path


@pytest.fixture
def mock_client() -> AIClient:
    settings = Settings(
        openai_api_key="",
        openai_base_url="https://api.openai.com/v1",
        openai_model="gpt-4o-mini",
    )
    return AIClient(settings, mock=True)


def test_extract_mock(mock_client: AIClient) -> None:
    resume = extract_resume("任意文本", mock_client)
    assert resume.name == "张明"
    assert "Python" in resume.skills


def test_score_mock(mock_client: AIClient) -> None:
    resume = extract_resume("任意文本", mock_client)
    score = score_resume(resume, "需要 Python 和 Agent 经验", mock_client)
    assert 0 <= score.overall_score <= 100
    assert score.skill_score <= 30
    assert len(score.interview_suggestions) > 0


def test_cli_extract_mock(tmp_path: Path) -> None:
    pdf = _make_sample_pdf(tmp_path)
    result = runner.invoke(app, ["extract", str(pdf), "--mock"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["name"] == "张明"


def test_cli_score_mock(tmp_path: Path) -> None:
    pdf = _make_sample_pdf(tmp_path)
    jd = tmp_path / "jd.txt"
    jd.write_text("Python AI Agent 3年经验", encoding="utf-8")
    result = runner.invoke(app, ["score", str(pdf), "--jd", str(jd), "--mock"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert "resume" in data
    assert "score" in data
    assert data["score"]["overall_score"] == 78


def test_cli_parse(tmp_path: Path) -> None:
    pdf = _make_sample_pdf(tmp_path)
    result = runner.invoke(app, ["parse", str(pdf)])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert "text" in data
    assert data["char_count"] > 0
