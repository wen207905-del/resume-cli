"""Typer CLI entry point for resume analysis."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from resume_cli.ai_client import AIClient, AIClientError
from resume_cli.config import ensure_api_key, get_settings, resolve_path
from resume_cli.extractor import extract_resume
from resume_cli.pdf_parser import PDFParseError, extract_text_from_pdf
from resume_cli.schemas import ExtractResult
from resume_cli.scorer import score_resume

app = typer.Typer(
    name="resume-cli",
    help="简历解析与 JD 匹配评分",
    add_completion=False,
)


def _write_output(data: dict, output: Optional[Path]) -> None:
    text = json.dumps(data, ensure_ascii=False, indent=2)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
        typer.echo(f"结果已保存: {output}")
    else:
        typer.echo(text)


def _read_jd(jd_path: Optional[Path], jd_text: Optional[str]) -> str:
    if jd_text:
        return jd_text.strip()
    if jd_path:
        path = resolve_path(jd_path)
        return path.read_text(encoding="utf-8").strip()
    raise typer.BadParameter("请通过 --jd 或 --jd-text 提供岗位描述")


def _handle_errors(exc: Exception) -> None:
    if isinstance(exc, PDFParseError):
        typer.secho(f"[PDF 错误] {exc}", fg=typer.colors.RED, err=True)
    elif isinstance(exc, AIClientError):
        typer.secho(f"[AI 错误] {exc}", fg=typer.colors.RED, err=True)
    elif isinstance(exc, FileNotFoundError):
        typer.secho(f"[文件错误] {exc}", fg=typer.colors.RED, err=True)
    elif isinstance(exc, ValueError):
        typer.secho(f"[配置错误] {exc}", fg=typer.colors.RED, err=True)
    else:
        typer.secho(f"[未知错误] {exc}", fg=typer.colors.RED, err=True)
    raise typer.Exit(code=1)


@app.command("check")
def check_cmd(
    mock: bool = typer.Option(False, "--mock", help="跳过 API 检测"),
) -> None:
    """检查 DeepSeek API 配置是否可用。"""
    try:
        settings = get_settings()
        ensure_api_key(settings, mock)
        typer.echo(f"模型: {settings.openai_model}")
        typer.echo(f"接口: {settings.openai_base_url}")
        if mock:
            typer.secho("mock 模式，跳过 API 检测", fg=typer.colors.GREEN)
            return
        client = AIClient(settings)
        reply = client.ping()
        typer.secho(f"API 连接正常，回复: {reply.strip()}", fg=typer.colors.GREEN)
    except Exception as exc:
        _handle_errors(exc)


@app.command("parse")
def parse_cmd(
    pdf: Path = typer.Argument(..., help="PDF 简历路径", exists=False),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="输出文件路径"),
) -> None:
    """从 PDF 简历提取纯文本。"""
    try:
        pdf_path = resolve_path(pdf)
        text = extract_text_from_pdf(pdf_path)
        result = {"source": str(pdf_path), "text": text, "char_count": len(text)}
        _write_output(result, output)
    except Exception as exc:
        _handle_errors(exc)


@app.command("extract")
def extract_cmd(
    pdf: Path = typer.Argument(..., help="PDF 简历路径", exists=False),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="输出 JSON 文件"),
    mock: bool = typer.Option(False, "--mock", help="模拟模式，不调用真实 API"),
) -> None:
    """从 PDF 简历抽取结构化 JSON。"""
    try:
        settings = get_settings()
        ensure_api_key(settings, mock)
        pdf_path = resolve_path(pdf)
        text = extract_text_from_pdf(pdf_path)
        client = AIClient(settings, mock=mock)
        resume = extract_resume(text, client, settings)
        _write_output(resume.model_dump(), output)
    except Exception as exc:
        _handle_errors(exc)


@app.command("score")
def score_cmd(
    pdf: Path = typer.Argument(..., help="PDF 简历路径", exists=False),
    jd: Optional[Path] = typer.Option(None, "--jd", help="JD 文本文件路径"),
    jd_text: Optional[str] = typer.Option(None, "--jd-text", help="JD 文本内容"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="输出 JSON 文件"),
    mock: bool = typer.Option(False, "--mock", help="模拟模式，不调用真实 API"),
) -> None:
    """结合 JD 对简历做匹配评分。"""
    try:
        settings = get_settings()
        ensure_api_key(settings, mock)
        pdf_path = resolve_path(pdf)
        jd_content = _read_jd(jd, jd_text)

        text = extract_text_from_pdf(pdf_path)
        client = AIClient(settings, mock=mock)
        resume = extract_resume(text, client, settings)
        score = score_resume(resume, jd_content, client)

        result = ExtractResult(resume=resume, score=score).model_dump()
        _write_output(result, output)
    except Exception as exc:
        _handle_errors(exc)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
