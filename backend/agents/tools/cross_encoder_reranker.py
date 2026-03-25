from __future__ import annotations

from sentence_transformers import CrossEncoder
from config import get_settings

settings = get_settings()

_cross_encoder: CrossEncoder | None = None  # type: ignore[type-arg]

CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


def get_cross_encoder() -> CrossEncoder:  # type: ignore[type-arg]
    global _cross_encoder
    if _cross_encoder is None:
        _cross_encoder = CrossEncoder(CROSS_ENCODER_MODEL)
    return _cross_encoder


def run_cross_encoder_reranker(
    query: str,
    chunks: list[dict],
    top_k: int = 5,
    threshold: float = 0.1,
) -> list[dict]:
    """
    LangGraph tool node: re-rank retrieved chunks using a cross-encoder.
    Returns top_k chunks above the relevance threshold, sorted by score.
    """
    if not chunks:
        return []

    ce = get_cross_encoder()
    contents = [str(c.get("payload", {}).get("content", "")) for c in chunks]
    pairs = [(query, content) for content in contents]
    scores: list[float] = ce.predict(pairs).tolist()  # type: ignore[attr-defined]

    scored = [(score, chunk) for score, chunk in zip(scores, chunks) if score >= threshold]
    scored.sort(key=lambda x: x[0], reverse=True)

    result = []
    for score, chunk in scored[:top_k]:
        chunk = dict(chunk)
        chunk["score"] = round(score, 4)
        result.append(chunk)
    return result
