"""DOCX to PDF conversion service with converter fallbacks."""

from __future__ import annotations

import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from docx2pdf import convert as docx2pdf_convert

from ..core.exceptions import ConversionError


def _find_generated_pdf(output_dir: Path, expected_stem: str) -> Path | None:
    """Find generated PDF, preferring the expected stem-based filename."""
    expected_file = output_dir / f"{expected_stem}.pdf"
    if expected_file.exists():
        return expected_file

    pdf_files = list(output_dir.glob("*.pdf"))
    if pdf_files:
        return pdf_files[0]

    return None


def _is_valid_pdf(pdf_path: Path) -> bool:
    """Validate PDF output is non-empty and has a PDF signature."""
    if not pdf_path.exists() or pdf_path.stat().st_size == 0:
        return False
    try:
        return pdf_path.read_bytes().startswith(b"%PDF")
    except Exception:
        return False


def _convert_with_docx2pdf(input_path: Path, output_dir: Path) -> Path | None:
    """Try converting using Microsoft Word automation via docx2pdf."""
    try:
        docx2pdf_convert(str(input_path), str(output_dir))
        candidate = _find_generated_pdf(output_dir, input_path.stem)
        if candidate and _is_valid_pdf(candidate):
            return candidate
        return None
    except Exception:
        return None


def _convert_with_libreoffice(input_path: Path, output_dir: Path) -> Path | None:
    """Fallback to LibreOffice CLI if available on the host machine."""
    for executable in ("soffice", "libreoffice"):
        try:
            command = [
                executable,
                "--headless",
                "--convert-to",
                "pdf",
                str(input_path),
                "--outdir",
                str(output_dir),
            ]
            completed = subprocess.run(command, check=False, capture_output=True, text=True)
            if completed.returncode != 0:
                continue

            candidate = _find_generated_pdf(output_dir, input_path.stem)
            if candidate and _is_valid_pdf(candidate):
                return candidate
        except Exception:
            continue

    return None


def convert_docx_to_pdf(docx_bytes: bytes) -> bytes:
    """Convert DOCX bytes to PDF bytes using temporary files with cleanup."""
    with TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        input_path = tmp_path / "input.docx"

        input_path.write_bytes(docx_bytes)

        output_pdf = _convert_with_docx2pdf(input_path, tmp_path)
        if output_pdf is None:
            output_pdf = _convert_with_libreoffice(input_path, tmp_path)

        if output_pdf is None:
            raise ConversionError(
                "Unable to convert DOCX to PDF. Install Microsoft Word (for docx2pdf) "
                "or LibreOffice CLI on the server."
            )

        return output_pdf.read_bytes()
