"""Security utilities for validating uploads and sanitizing file names."""

from __future__ import annotations

import re
import zipfile
from io import BytesIO
from pathlib import Path

from .exceptions import ValidationError

SAFE_FILENAME_PATTERN = re.compile(r"[^A-Za-z0-9._-]+")


def sanitize_filename(filename: str) -> str:
    """Remove unsafe characters and keep a safe fallback name."""
    raw_name = Path(filename).name.strip()
    safe_name = SAFE_FILENAME_PATTERN.sub("_", raw_name)
    return safe_name or "uploaded_file"


def ensure_extension(filename: str, expected_extension: str) -> None:
    """Reject files that do not match the expected extension."""
    if not filename.lower().endswith(expected_extension.lower()):
        raise ValidationError(f"Only {expected_extension} files are allowed.")


def is_pdf_signature(file_bytes: bytes) -> bool:
    """Basic PDF signature check to block spoofed uploads."""
    return file_bytes.startswith(b"%PDF")


def is_docx_signature(file_bytes: bytes) -> bool:
    """Check DOCX structure by inspecting ZIP entries."""
    try:
        with zipfile.ZipFile(BytesIO(file_bytes), "r") as archive:
            names = set(archive.namelist())
            has_content_types = "[Content_Types].xml" in names
            has_word_dir = any(name.startswith("word/") for name in names)
            return has_content_types and has_word_dir
    except Exception:
        return False


def validate_file_content(file_bytes: bytes, expected_type: str) -> None:
    """Validate file signatures for supported input formats."""
    if not file_bytes:
        raise ValidationError("Uploaded file is empty.")

    if expected_type == "pdf" and not is_pdf_signature(file_bytes):
        raise ValidationError("Invalid PDF file content.")

    if expected_type == "docx" and not is_docx_signature(file_bytes):
        raise ValidationError("Invalid DOCX file content.")
