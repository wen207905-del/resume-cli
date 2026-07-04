"""PDF resume text extraction using PyMuPDF."""

from __future__ import annotations

from pathlib import Path

import fitz  # PyMuPDF


class PDFParseError(Exception):
    """Raised when PDF cannot be read or parsed."""


def extract_text_from_pdf(pdf_path: str | Path) -> str:
    path = Path(pdf_path)
    if not path.exists():
        raise PDFParseError(f"PDF 文件不存在: {path}")
    if path.suffix.lower() != ".pdf":
        raise PDFParseError(f"不是 PDF 文件: {path}")

    try:
        doc = fitz.open(path)
    except Exception as exc:
        raise PDFParseError(f"无法打开 PDF 文件: {path} — {exc}") from exc

    try:
        pages: list[str] = []
        for page in doc:
            text = page.get_text("text")
            if text.strip():
                pages.append(text.strip())
        if not pages:
            raise PDFParseError(f"PDF 未提取到文本（可能是扫描件）: {path}")
        return clean_text("\n\n".join(pages))
    finally:
        doc.close()


def clean_text(raw: str) -> str:
    """Normalize whitespace and common PDF artifacts."""
    lines = [line.strip() for line in raw.splitlines()]
    lines = [line for line in lines if line]
    text = "\n".join(lines)
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")
    return text.strip()
