from __future__ import annotations

import logging

from celery import Celery
from celery.signals import worker_init

from config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

celery_app = Celery(
    "multimodal_rag",
    broker=settings.rabbitmq_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)


@worker_init.connect
def warmup_ocr(**kwargs) -> None:  # type: ignore[no-untyped-def]
    """
    Pre-load PaddleOCR on worker startup so the first ingestion request
    doesn't incur a 15–30 second cold-start penalty.
    """
    try:
        from paddleocr import PaddleOCR  # type: ignore[import]

        logger.info("Warming up PaddleOCR model …")
        PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
        logger.info("PaddleOCR warm-up complete")
    except ImportError:
        logger.warning("PaddleOCR not installed — OCR will fall back to Tesseract")
    except Exception as exc:
        logger.warning("PaddleOCR warm-up failed: %s — will fallback to Tesseract at runtime", exc)
