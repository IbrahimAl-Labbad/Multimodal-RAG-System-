from __future__ import annotations

import base64
import io

import httpx
from PIL import Image as PILImage

from config import get_settings

settings = get_settings()


async def caption_image(image: PILImage.Image) -> str:
    """
    Send an image to LLaVA via Ollama for captioning / VQA.

    LLaVA is used ONLY for image understanding and generation — NOT for embeddings.
    For embeddings, use models/embeddings.py (CLIP/SigLIP).
    """
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    b64_image = base64.b64encode(buffered.getvalue()).decode("utf-8")

    payload = {
        "model": settings.vision_model,  # Read from env — never hardcoded
        "prompt": "Describe this image in detail. Focus on text, charts, diagrams, and key visual elements.",
        "images": [b64_image],
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{settings.ollama_base_url}/api/generate",
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        return str(data.get("response", ""))


async def answer_visual_question(image: PILImage.Image, question: str) -> str:
    """Visual question answering via LLaVA through Ollama."""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    b64_image = base64.b64encode(buffered.getvalue()).decode("utf-8")

    payload = {
        "model": settings.vision_model,
        "prompt": question,
        "images": [b64_image],
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{settings.ollama_base_url}/api/generate",
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        return str(data.get("response", ""))
