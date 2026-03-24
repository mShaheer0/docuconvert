"""File utilities for safe upload reads and API download metadata."""

from __future__ import annotations

from urllib.parse import quote
from pathlib import Path

from fastapi import UploadFile

from ..core.exceptions import ValidationError
from ..core.security import sanitize_filename
from ..core.settings import CHUNK_SIZE_BYTES


def human_file_size(size_bytes: int) -> str:
    """Return human-readable file size for logs or debug output."""
    units = ["B", "KB", "MB", "GB"]
    value = float(size_bytes)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.2f} {unit}"
        value /= 1024
    return f"{size_bytes} B"


async def read_upload_bytes(upload_file: UploadFile, max_size_bytes: int) -> bytes:
    """Read uploaded file in chunks while enforcing a strict max size."""
    total_size = 0
    chunks: list[bytes] = []

    while True:
        chunk = await upload_file.read(CHUNK_SIZE_BYTES)
        if not chunk:
            break
        total_size += len(chunk)
        if total_size > max_size_bytes:
            raise ValidationError("File is too large. Maximum allowed size is 10 MB.")
        chunks.append(chunk)

    await upload_file.close()

    if total_size == 0:
        raise ValidationError("Uploaded file is empty.")

    return b"".join(chunks)


def make_output_filename(input_filename: str, new_extension: str) -> str:
    """Generate a sanitized output filename with a new extension."""
    safe_name = sanitize_filename(input_filename)
    stem = Path(safe_name).stem
    return f"{stem}.{new_extension}"


def content_disposition(filename: str) -> str:
    """Create an attachment header value for download responses."""
    safe_quoted = quote(filename)
    return f'attachment; filename="{filename}"; filename*=UTF-8\'\'{safe_quoted}'
