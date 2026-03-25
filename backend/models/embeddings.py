from __future__ import annotations

from functools import lru_cache

import torch
from PIL import Image as PILImage
from sentence_transformers import SentenceTransformer
from transformers import CLIPModel, CLIPProcessor

from config import get_settings

settings = get_settings()


@lru_cache(maxsize=1)
def get_text_embedder() -> SentenceTransformer:
    return SentenceTransformer(settings.embedding_model)


@lru_cache(maxsize=1)
def get_clip_model() -> tuple[CLIPModel, CLIPProcessor]:  # type: ignore[type-arg]
    model = CLIPModel.from_pretrained(settings.clip_model)  # type: ignore[attr-defined]
    processor = CLIPProcessor.from_pretrained(settings.clip_model)  # type: ignore[attr-defined]
    return model, processor  # type: ignore[return-value]


def embed_text(text: str) -> list[float]:
    """Embed a text string using SentenceTransformers."""
    embedder = get_text_embedder()
    vector: list[float] = embedder.encode(text, normalize_embeddings=True).tolist()
    return vector


def embed_image(image: PILImage.Image) -> list[float]:
    """Embed an image using CLIP/SigLIP (for vector similarity — NOT for generation)."""
    model, processor = get_clip_model()
    inputs = processor(images=image, return_tensors="pt")
    with torch.no_grad():
        features = model.get_image_features(**inputs)  # type: ignore[operator]
        features = features / features.norm(dim=-1, keepdim=True)
    return features.squeeze().cpu().tolist()


def embed_text_clip(text: str) -> list[float]:
    """Embed text using CLIP's text encoder (for cross-modal similarity search)."""
    model, processor = get_clip_model()
    inputs = processor(text=[text], return_tensors="pt", padding=True)
    with torch.no_grad():
        features = model.get_text_features(**inputs)  # type: ignore[operator]
        features = features / features.norm(dim=-1, keepdim=True)
    return features.squeeze().cpu().tolist()
