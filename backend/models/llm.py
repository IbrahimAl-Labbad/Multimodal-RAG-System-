from __future__ import annotations

from collections.abc import AsyncIterator

import httpx

from config import get_settings

settings = get_settings()


async def generate_stream(prompt: str, context: str) -> AsyncIterator[str]:
    """Stream tokens from Ollama using the MODEL_NAME env var."""
    system = (
        "You are a helpful assistant answering questions based strictly on the provided context. "
        "If the context does not contain enough information, say so clearly."
    )
    full_prompt = f"Context:\n{context}\n\nQuestion: {prompt}"

    payload = {
        "model": settings.model_name,  # Never hardcoded — always from env
        "prompt": full_prompt,
        "system": system,
        "stream": True,
        "options": {"temperature": 0.1, "top_p": 0.9},
    }

    async with httpx.AsyncClient(timeout=300.0) as client:
        async with client.stream(
            "POST",
            f"{settings.ollama_base_url}/api/generate",
            json=payload,
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line:
                    import json

                    data = json.loads(line)
                    token = data.get("response", "")
                    if token:
                        yield token
                    if data.get("done", False):
                        break


async def generate(prompt: str, context: str) -> str:
    """Non-streaming generation from Ollama."""
    tokens: list[str] = []
    async for token in generate_stream(prompt, context):
        tokens.append(token)
    return "".join(tokens)
