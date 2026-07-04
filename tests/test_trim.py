"""Tests for text trimming."""

from resume_cli.extractor import trim_resume_text


def test_trim_short_text() -> None:
    assert trim_resume_text("hello", 100) == "hello"


def test_trim_long_text() -> None:
    text = "a" * 200
    result = trim_resume_text(text, 100)
    assert len(result) < 200
    assert "已截断" in result
