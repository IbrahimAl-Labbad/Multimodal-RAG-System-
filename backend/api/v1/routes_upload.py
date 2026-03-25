from __future__ import annotations

import uuid
from fastapi import APIRouter, File, HTTPException, Request, UploadFile, status
from schemas.response import UploadResponse
from config import get_settings

settings = get_settings()
router = APIRouter(tags=["upload"])


@router.post("/upload", response_model=UploadResponse)
async def upload_file(request: Request, file: UploadFile = File(...)) -> UploadResponse:
    # ── Validate extension ────────────────────────────────────────────────────
    ext = (file.filename or "").rsplit(".", 1)[-1].lower()
    if ext not in settings.allowed_extensions_set:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File type '.{ext}' not allowed. Allowed: {settings.allowed_extensions}",
        )

    # ── Validate size ─────────────────────────────────────────────────────────
    file_bytes = await file.read()
    if len(file_bytes) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum size of {settings.max_upload_size_mb}MB",
        )

    document_id = uuid.uuid4()
    return UploadResponse(
        document_id=document_id,
        filename=file.filename or "unknown",
        size_bytes=len(file_bytes),
    )
