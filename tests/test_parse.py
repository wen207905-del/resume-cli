"""Tests for PDF parsing."""

from __future__ import annotations

from pathlib import Path

import fitz
import pytest

from resume_cli.pdf_parser import PDFParseError, clean_text, extract_text_from_pdf


def _make_sample_pdf(tmp_path: Path, text: str) -> Path:
    pdf_path = tmp_path / "sample.pdf"
    doc = fitz.open()
    page = doc.new_page()
    # china-s 字体支持中文，避免 Windows 下乱码
    page.insert_text((72, 72), text, fontsize=12, fontname="china-s")
    doc.save(pdf_path)
    doc.close()
    return pdf_path


SAMPLE_TEXT = """张明
电话：13800138000
邮箱：zhangming@example.com

工作经历
某某科技 | Python开发 | 2022-至今
负责文档解析与 API 对接

技能：Python, FastAPI, PyMuPDF
"""


def test_extract_text_from_pdf(tmp_path: Path) -> None:
    pdf_path = _make_sample_pdf(tmp_path, SAMPLE_TEXT)
    result = extract_text_from_pdf(pdf_path)
    assert "张明" in result
    assert "Python" in result


def test_pdf_not_found() -> None:
    with pytest.raises(PDFParseError, match="不存在"):
        extract_text_from_pdf("/nonexistent/resume.pdf")


def test_not_pdf_file(tmp_path: Path) -> None:
    txt = tmp_path / "resume.txt"
    txt.write_text("hello", encoding="utf-8")
    with pytest.raises(PDFParseError, match="不是 PDF"):
        extract_text_from_pdf(txt)


def test_clean_text() -> None:
    raw = "  hello  \n\n\n\n  world  \n  "
    assert clean_text(raw) == "hello\nworld"
