"""FastAPI entrypoint with API routers and static frontend routes."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .core.exceptions import AppError
from .core.settings import RATE_LIMIT_MAX_REQUESTS, RATE_LIMIT_WINDOW_SECONDS
from .middlewares.rate_limit import RateLimitMiddleware
from .routes.pdf_to_word import router as pdf_to_word_router
from .routes.word_to_pdf import router as word_to_pdf_router
from .routes.contact import router as contact_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(title="File Converter API", version="1.0.0")


def _get_cors_origins() -> list[str]:
    """Read allowed frontend origins from env for cross-domain deployments."""
    raw = os.getenv("FRONTEND_ORIGINS", "")
    if not raw.strip():
        return ["*"]
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


app.add_middleware(
    CORSMiddleware,
    allow_origins=_get_cors_origins(),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    RateLimitMiddleware,
    max_requests=RATE_LIMIT_MAX_REQUESTS,
    window_seconds=RATE_LIMIT_WINDOW_SECONDS,
)

app.include_router(pdf_to_word_router)
app.include_router(word_to_pdf_router)
app.include_router(contact_router)

app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")


@app.exception_handler(AppError)
async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    """Return safe public messages for known application errors."""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.exception_handler(Exception)
async def global_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    """Hide internal details from clients while logging for operators."""
    logger.exception("Unhandled server error: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "An unexpected error occurred."})


@app.get("/", include_in_schema=False)
async def root() -> FileResponse:
    """Serve the landing page with available conversion options."""
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/pdf-to-word", include_in_schema=False)
async def pdf_to_word_page() -> FileResponse:
    """Serve the PDF to Word frontend page."""
    return FileResponse(FRONTEND_DIR / "pdf-to-word.html")


@app.get("/pdf-to-word.html", include_in_schema=False)
async def pdf_to_word_page_alias() -> FileResponse:
    """Serve PDF to Word page using .html alias URL."""
    return FileResponse(FRONTEND_DIR / "pdf-to-word.html")


@app.get("/word-to-pdf", include_in_schema=False)
async def word_to_pdf_page() -> FileResponse:
    """Serve the Word to PDF frontend page."""
    return FileResponse(FRONTEND_DIR / "word-to-pdf.html")


@app.get("/word-to-pdf.html", include_in_schema=False)
async def word_to_pdf_page_alias() -> FileResponse:
    """Serve Word to PDF page using .html alias URL."""
    return FileResponse(FRONTEND_DIR / "word-to-pdf.html")


@app.get("/robots.txt", include_in_schema=False)
async def robots() -> FileResponse:
    """Serve robots.txt for search engine crawling."""
    return FileResponse(FRONTEND_DIR / "robots.txt", media_type="text/plain")


@app.get("/sitemap.xml", include_in_schema=False)
async def sitemap() -> FileResponse:
    """Serve sitemap.xml for search engine indexing."""
    return FileResponse(FRONTEND_DIR / "sitemap.xml", media_type="application/xml")


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """Simple health endpoint for monitoring and orchestration."""
    return {"status": "ok"}
