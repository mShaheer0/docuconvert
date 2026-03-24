"""Routes for PDF to DOCX conversion."""

from __future__ import annotations

from io import BytesIO

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import StreamingResponse

from ..core.security import ensure_extension, validate_file_content
from ..core.settings import MAX_FILE_SIZE_BYTES
from ..services.pdf_to_word_service import convert_pdf_to_docx
from ..utils.file_utils import content_disposition, make_output_filename, read_upload_bytes

router = APIRouter(prefix="/api/pdf-to-word", tags=["pdf-to-word"])


@router.post("/convert")
async def convert_pdf(uploaded_file: UploadFile = File(...)) -> StreamingResponse:
    """Convert an uploaded PDF file to DOCX."""
    ensure_extension(uploaded_file.filename or "", ".pdf")
    file_bytes = await read_upload_bytes(uploaded_file, MAX_FILE_SIZE_BYTES)
    validate_file_content(file_bytes, expected_type="pdf")

    docx_bytes = convert_pdf_to_docx(file_bytes)
    output_name = make_output_filename(uploaded_file.filename or "converted.pdf", "docx")

    return StreamingResponse(
        BytesIO(docx_bytes),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": content_disposition(output_name)},
    )
