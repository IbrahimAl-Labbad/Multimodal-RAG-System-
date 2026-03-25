from __future__ import annotations

import io
from PIL import Image as PILImage
from models.vision import caption_image, answer_visual_question


async def run_image_analyzer(image_bytes: bytes, question: str | None = None) -> str:
    """LangGraph tool node: caption or answer questions about an image using LLaVA via Ollama."""
    pil_img = PILImage.open(io.BytesIO(image_bytes)).convert("RGB")
    if question:
        return await answer_visual_question(pil_img, question)
    return await caption_image(pil_img)
