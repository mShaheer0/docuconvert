"""Routes for DOCX to PDF conversion."""

from __future__ import annotations

from io import BytesIO

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import StreamingResponse

from ..core.security import ensure_extension, validate_file_content
from ..core.settings import MAX_FILE_SIZE_BYTES
from ..services.word_to_pdf_service import convert_docx_to_pdf
from ..utils.file_utils import content_disposition, make_output_filename, read_upload_bytes

router = APIRouter(prefix="/api/word-to-pdf", tags=["word-to-pdf"])


@router.post("/convert")
async def convert_docx(uploaded_file: UploadFile = File(...)) -> StreamingResponse:
    """Convert an uploaded DOCX file to PDF."""
    ensure_extension(uploaded_file.filename or "", ".docx")
    file_bytes = await read_upload_bytes(uploaded_file, MAX_FILE_SIZE_BYTES)
    validate_file_content(file_bytes, expected_type="docx")

    pdf_bytes = convert_docx_to_pdf(file_bytes)
    output_name = make_output_filename(uploaded_file.filename or "converted.docx", "pdf")

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": content_disposition(output_name)},
    )
