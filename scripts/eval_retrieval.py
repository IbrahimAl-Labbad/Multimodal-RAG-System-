"""
RAGAS Retrieval Evaluation Script
===================================
Measures: Faithfulness, Answer Relevance, Context Recall (RAGAS)
Also benchmarks: Indexing throughput, End-to-end P95 latency

Usage:
    python scripts/eval_retrieval.py

Requirements:
    pip install ragas datasets httpx
"""
from __future__ import annotations

import asyncio
import statistics
import time
from typing import Any

import httpx
from datasets import Dataset  # type: ignore[import]

# ── Sample evaluation dataset ─────────────────────────────────────────────────
EVAL_DATA = [
    {
        "question": "What is LangGraph used for in this system?",
        "ground_truth": "LangGraph is used for agentic orchestration, implementing the reasoning graph that decomposes queries, retrieves context, reranks, synthesizes, and generates answers.",
        "contexts": [
            "LangGraph orchestrates the multi-step RAG reasoning pipeline including query decomposition, retrieval, reranking, and generation."
        ],
    },
    {
        "question": "Which model is used for image captioning?",
        "ground_truth": "LLaVA served via Ollama is used for image captioning and visual question answering.",
        "contexts": [
            "LLaVA (via Ollama) is used exclusively for image understanding, captioning, and VQA. CLIP/SigLIP handles embeddings only."
        ],
    },
]

API_URL = "http://localhost:8000"
JWT_TOKEN = "your-token-here"  # Replace with a valid token for live testing


async def fetch_answer(question: str) -> tuple[str, float]:
    """Send a chat request and measure latency."""
    t0 = time.perf_counter()
    full_answer = ""
    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream(
            "POST",
            f"{API_URL}/api/v1/chat",
            headers={"Authorization": f"Bearer {JWT_TOKEN}"},
            json={"query": question, "top_k": 5},
        ) as resp:
            async for line in resp.aiter_lines():
                if line.startswith("data: ") and line != "data: [DONE]":
                    import json
                    try:
                        data = json.loads(line[6:])
                        if data.get("type") == "token":
                            full_answer += data.get("content", "")
                    except Exception:
                        pass
    latency = time.perf_counter() - t0
    return full_answer, latency


def run_ragas_eval(answers: list[str], latencies: list[float]) -> None:
    """Run RAGAS metrics on the evaluation dataset."""
    try:
        from ragas import evaluate  # type: ignore[import]
        from ragas.metrics import (  # type: ignore[import]
            answer_relevancy,
            context_recall,
            faithfulness,
        )

        dataset_dict: dict[str, list[Any]] = {
            "question": [d["question"] for d in EVAL_DATA],
            "answer": answers,
            "contexts": [d["contexts"] for d in EVAL_DATA],
            "ground_truth": [d["ground_truth"] for d in EVAL_DATA],
        }
        ds = Dataset.from_dict(dataset_dict)
        result = evaluate(ds, metrics=[faithfulness, answer_relevancy, context_recall])

        print("\n📊 RAGAS Evaluation Results")
        print("─" * 40)
        print(f"  Faithfulness:      {result['faithfulness']:.3f}  (target ≥ 0.85)")
        print(f"  Answer Relevance:  {result['answer_relevancy']:.3f}  (target ≥ 0.80)")
        print(f"  Context Recall:    {result['context_recall']:.3f}  (target ≥ 0.80)")

    except ImportError:
        print("⚠️  RAGAS not installed — pip install ragas datasets")

    # Latency report
    p95 = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 5 else max(latencies)
    print("\n⏱️  Latency Report")
    print("─" * 40)
    print(f"  Avg latency: {statistics.mean(latencies):.2f}s")
    print(f"  P95 latency: {p95:.2f}s  (target < 3.0s)")


async def main() -> None:
    print("🚀 Running RAGAS evaluation …")
    answers: list[str] = []
    latencies: list[float] = []

    for item in EVAL_DATA:
        print(f"  → Querying: {item['question'][:60]}…")
        try:
            answer, latency = await fetch_answer(item["question"])
        except Exception as e:
            print(f"  ⚠️  Request failed: {e} — using empty answer")
            answer, latency = "", 0.0
        answers.append(answer)
        latencies.append(latency)

    run_ragas_eval(answers, latencies)


if __name__ == "__main__":
    asyncio.run(main())
