from __future__ import annotations

import io
import time
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import fitz  # PyMuPDF
from PIL import Image as PILImage
from unstructured.partition.pdf import partition_pdf

from config import get_settings
from models.embeddings import embed_text, embed_image
from models.vision import caption_image
from schemas.document import (
    ChunkType,
    DocumentMetadata,
    ImageChunk,
    IngestionResult,
    TableChunk,
    TextChunk,
)
from storage.qdrant_client import ensure_collection, get_qdrant_client, upsert_points

settings = get_settings()

TEXT_CHUNK_SIZE = 512  # tokens (approximate characters / 4)
TEXT_OVERLAP = 64


def _ocr_page(page: fitz.Page) -> str:  # type: ignore[name-defined]
    """OCR a PDF page using PaddleOCR with Tesseract fallback."""
    pix = page.get_pixmap(dpi=200)
    img = PILImage.frombytes("RGB", [pix.width, pix.height], pix.samples)
    try:
        from paddleocr import PaddleOCR  # type: ignore[import]
        ocr = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
        import numpy as np
        result = ocr.ocr(np.array(img), cls=True)
        lines = [line[1][0] for block in result for line in block if line]
        return "\n".join(lines)
    except Exception:
        import pytesseract
        return pytesseract.image_to_string(img)


def _chunk_text(text: str, source_meta: dict[str, Any]) -> list[dict[str, Any]]:
    """Split text into overlapping chunks."""
    words = text.split()
    chunks: list[dict[str, Any]] = []
    step = TEXT_CHUNK_SIZE - TEXT_OVERLAP
    for i in range(0, len(words), step):
        chunk_words = words[i : i + TEXT_CHUNK_SIZE]
        chunks.append({"text": " ".join(chunk_words), **source_meta})
    return chunks


async def ingest_pdf(
    file_bytes: bytes,
    filename: str,
    document_id: UUID | None = None,
) -> IngestionResult:
    """Full PDF ingestion: parse → OCR → caption → embed → upsert to Qdrant."""
    t0 = time.perf_counter()
    document_id = document_id or uuid4()

    # ── Parse structure via Unstructured ──────────────────────────────────────
    elements = partition_pdf(file=io.BytesIO(file_bytes), strategy="hi_res")

    text_points: list[dict[str, Any]] = []
    image_points: list[dict[str, Any]] = []
    table_points: list[dict[str, Any]] = []

    page_texts: dict[int, list[str]] = {}

    for el in elements:
        el_type = type(el).__name__
        page = getattr(el, "page_number", 1) or 1

        if el_type == "Table":
            content = str(el)
            meta = DocumentMetadata(
                document_id=document_id,
                filename=filename,
                page_number=page,
                chunk_type=ChunkType.TABLE,
            )
            embedding = embed_text(content)
            table_points.append({
                "id": str(uuid4()),
                "vector": embedding,
                "payload": {**meta.model_dump(mode="json"), "content": content},
            })
        elif el_type in ("Image",):
            pass  # Images extracted separately via PyMuPDF below
        else:
            page_texts.setdefault(page, []).append(str(el))

    # ── Text chunking ─────────────────────────────────────────────────────────
    for page, texts in page_texts.items():
        combined = " ".join(texts)
        for chunk_data in _chunk_text(combined, {}):
            meta = DocumentMetadata(
                document_id=document_id,
                filename=filename,
                page_number=page,
                chunk_type=ChunkType.TEXT,
            )
            embedding = embed_text(chunk_data["text"])
            text_points.append({
                "id": str(uuid4()),
                "vector": embedding,
                "payload": {**meta.model_dump(mode="json"), "content": chunk_data["text"]},
            })

    # ── Image extraction via PyMuPDF → LLaVA captioning ──────────────────────
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    for page_num, page in enumerate(doc, start=1):
        if not page_texts.get(page_num):
            # Scanned page — OCR it
            ocr_text = _ocr_page(page)
            if ocr_text.strip():
                meta = DocumentMetadata(
                    document_id=document_id,
                    filename=filename,
                    page_number=page_num,
                    chunk_type=ChunkType.OCR,
                )
                embedding = embed_text(ocr_text)
                text_points.append({
                    "id": str(uuid4()),
                    "vector": embedding,
                    "payload": {**meta.model_dump(mode="json"), "content": ocr_text},
                })

        for img_index, img_info in enumerate(page.get_images(full=True)):
            xref = img_info[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            pil_img = PILImage.open(io.BytesIO(image_bytes)).convert("RGB")

            caption = await caption_image(pil_img)
            embedding = embed_image(pil_img)

            meta = DocumentMetadata(
                document_id=document_id,
                filename=filename,
                page_number=page_num,
                chunk_type=ChunkType.IMAGE,
            )
            image_points.append({
                "id": str(uuid4()),
                "vector": embedding,
                "payload": {
                    **meta.model_dump(mode="json"),
                    "caption": caption,
                    "content": caption,
                },
            })

    # ── Upsert to Qdrant ──────────────────────────────────────────────────────
    client = get_qdrant_client()
    vector_size = len(text_points[0]["vector"]) if text_points else 384
    await ensure_collection(client, settings.qdrant_collection, vector_size)

    all_points = text_points + table_points + image_points
    if all_points:
        await upsert_points(settings.qdrant_collection, all_points)

    elapsed = time.perf_counter() - t0
    return IngestionResult(
        document_id=document_id,
        filename=filename,
        text_chunks=len(text_points),
        image_chunks=len(image_points),
        table_chunks=len(table_points),
        total_chunks=len(all_points),
        elapsed_seconds=round(elapsed, 2),
    )


async def ingest_image(
    file_bytes: bytes,
    filename: str,
    document_id: UUID | None = None,
) -> IngestionResult:
    """Ingest a standalone image: caption via LLaVA → CLIP embed → upsert."""
    t0 = time.perf_counter()
    document_id = document_id or uuid4()

    pil_img = PILImage.open(io.BytesIO(file_bytes)).convert("RGB")
    caption = await caption_image(pil_img)
    embedding = embed_image(pil_img)

    meta = DocumentMetadata(
        document_id=document_id,
        filename=filename,
        chunk_type=ChunkType.IMAGE,
    )

    client = get_qdrant_client()
    await ensure_collection(client, settings.qdrant_collection, len(embedding))
    await upsert_points(settings.qdrant_collection, [{
        "id": str(uuid4()),
        "vector": embedding,
        "payload": {**meta.model_dump(mode="json"), "caption": caption, "content": caption},
    }])

    elapsed = time.perf_counter() - t0
    return IngestionResult(
        document_id=document_id,
        filename=filename,
        image_chunks=1,
        total_chunks=1,
        elapsed_seconds=round(elapsed, 2),
    )
