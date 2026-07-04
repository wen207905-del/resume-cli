"""FastAPI web server with drag-and-drop resume upload."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from resume_cli.ai_client import AIClientError
from resume_cli.config import ensure_api_key, get_settings
from resume_cli.pdf_parser import PDFParseError
from resume_cli.service import run_extract, run_score

STATIC_DIR = Path(__file__).parent / "static"
MAX_UPLOAD = 10 * 1024 * 1024  # 10MB


def create_app(mock: bool = False) -> FastAPI:
    app = FastAPI(title="Resume CLI", version="0.1.0")
    app.state.mock = mock

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/api/health")
    def health() -> dict:
        settings = get_settings()
        return {
            "ok": True,
            "model": settings.openai_model,
            "mock": app.state.mock,
        }

    @app.post("/api/extract")
    async def extract(file: UploadFile = File(...)) -> dict:
        content = await _read_pdf(file)
        try:
            settings = get_settings()
            ensure_api_key(settings, app.state.mock)
            resume = run_extract(content, settings, mock=app.state.mock)
            return {"ok": True, "data": resume.model_dump()}
        except (PDFParseError, AIClientError, ValueError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/api/score")
    async def score(
        file: UploadFile = File(...),
        jd: str = Form(...),
    ) -> dict:
        if not jd.strip():
            raise HTTPException(status_code=400, detail="请填写岗位描述 JD")
        content = await _read_pdf(file)
        try:
            settings = get_settings()
            ensure_api_key(settings, app.state.mock)
            result = run_score(content, jd, settings, mock=app.state.mock)
            return {"ok": True, "data": result.model_dump()}
        except (PDFParseError, AIClientError, ValueError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    return app


async def _read_pdf(file: UploadFile) -> bytes:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="请上传 PDF 文件")
    content = await file.read()
    if len(content) > MAX_UPLOAD:
        raise HTTPException(status_code=400, detail="文件不能超过 10MB")
    if not content:
        raise HTTPException(status_code=400, detail="文件为空")
    return content
