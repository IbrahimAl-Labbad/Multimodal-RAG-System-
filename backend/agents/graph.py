from __future__ import annotations

import re
from typing import Any, TypedDict
from uuid import UUID

from langgraph.graph import END, StateGraph

from agents.tools.cross_encoder_reranker import run_cross_encoder_reranker
from agents.tools.memory_manager import append_session_memory, get_session_memory
from agents.tools.vector_retriever import run_vector_retriever
from models.llm import generate
from schemas.query import QueryType


class AgentState(TypedDict):
    query: str
    session_id: str
    query_type: QueryType
    sub_queries: list[str]
    retrieved_chunks: list[dict[str, Any]]
    reranked_chunks: list[dict[str, Any]]
    context: str
    answer: str
    verified: bool
    citations: list[dict[str, Any]]
    document_ids: list[str] | None
    top_k: int


# ── Step 1: Decomposition ────────────────────────────────────────────────────

async def decompose(state: AgentState) -> AgentState:
    """Break complex queries into sub-queries."""
    query = state["query"]
    # Simple heuristic: split on conjunctions; in production use LLM sub-query generation
    sub_queries = [q.strip() for q in re.split(r"\band\b|\balso\b|;", query, flags=re.I) if q.strip()]
    if not sub_queries:
        sub_queries = [query]
    state["sub_queries"] = sub_queries
    return state


# ── Step 2: Retrieval ─────────────────────────────────────────────────────────

async def retrieval(state: AgentState) -> AgentState:
    """Retrieve chunks for all sub-queries and deduplicate by chunk id."""
    all_chunks: dict[str, dict[str, Any]] = {}
    for sub_q in state["sub_queries"]:
        chunks = await run_vector_retriever(
            query=sub_q,
            query_type=state.get("query_type", QueryType.TEXT),
            top_k=state.get("top_k", 5),
            document_ids=state.get("document_ids"),
        )
        for chunk in chunks:
            chunk_id = str(chunk.get("id", ""))
            if chunk_id not in all_chunks:
                all_chunks[chunk_id] = chunk
    state["retrieved_chunks"] = list(all_chunks.values())
    return state


# ── Step 3: Reranking ─────────────────────────────────────────────────────────

async def reranking(state: AgentState) -> AgentState:
    """Re-rank retrieved chunks with cross-encoder."""
    state["reranked_chunks"] = run_cross_encoder_reranker(
        query=state["query"],
        chunks=state["retrieved_chunks"],
        top_k=state.get("top_k", 5),
    )
    return state


# ── Step 4: Synthesis ─────────────────────────────────────────────────────────

async def synthesis(state: AgentState) -> AgentState:
    """Assemble context string from reranked chunks."""
    parts: list[str] = []
    for i, chunk in enumerate(state["reranked_chunks"], start=1):
        payload = chunk.get("payload", {})
        content = payload.get("content", payload.get("caption", ""))
        parts.append(f"[{i}] {content}")
    state["context"] = "\n\n".join(parts)
    return state


# ── Step 5: Generation ────────────────────────────────────────────────────────

async def generation(state: AgentState) -> AgentState:
    """Generate answer from context via Ollama."""
    # Prepend session history for multi-turn awareness
    history = await get_session_memory(UUID(state["session_id"]))
    history_text = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in history[-6:])
    enriched_query = f"{history_text}\nUSER: {state['query']}" if history_text else state["query"]

    answer = await generate(enriched_query, state["context"])
    state["answer"] = answer
    return state


# ── Step 6: Self-Verification ─────────────────────────────────────────────────

GROUNDING_THRESHOLD = 0.3  # Minimum fraction of claim n-grams found in context


def _extract_ngrams(text: str, n: int = 3) -> set[str]:
    """Extract n-gram sequences from text for overlap checking."""
    words = [w.lower().strip(".,;:!?\"'()[]") for w in text.split() if len(w) > 2]
    return {" ".join(words[i : i + n]) for i in range(len(words) - n + 1)}


def _compute_grounding_score(answer: str, chunk_contents: list[str]) -> float:
    """
    Explicit grounding: extract 3-grams from the answer, check how many
    appear verbatim in at least one retrieved chunk's content.
    Returns the fraction of answer n-grams found in context (0.0–1.0).
    """
    answer_ngrams = _extract_ngrams(answer, n=3)
    if not answer_ngrams:
        return 1.0  # trivially grounded (very short answer)

    # Build a single searchable text from all chunk contents
    context_text = " ".join(c.lower() for c in chunk_contents)

    grounded = sum(1 for ng in answer_ngrams if ng in context_text)
    return grounded / len(answer_ngrams)


async def self_verify(state: AgentState) -> AgentState:
    """
    Explicit grounding verification:
    1. Extract 3-gram phrases from the answer
    2. Check each against the actual retrieved chunk contents (not just context string)
    3. If grounding ratio < threshold, regenerate with a constrained prompt
    """
    answer = state.get("answer", "")
    reranked = state.get("reranked_chunks", [])

    # Extract raw content from each chunk for comparison
    chunk_contents = [
        str(c.get("payload", {}).get("content", c.get("payload", {}).get("caption", "")))
        for c in reranked
    ]

    score = _compute_grounding_score(answer, chunk_contents)
    state["verified"] = score >= GROUNDING_THRESHOLD

    # If poorly grounded, regenerate with a tighter constraint
    if not state["verified"] and chunk_contents:
        constrained_answer = await generate(
            f"Answer ONLY using information from the provided context. "
            f"If the context does not contain the answer, say 'I cannot find this in the provided documents.'\n\n"
            f"Question: {state['query']}",
            state["context"],
        )
        # Re-check grounding on the constrained answer
        new_score = _compute_grounding_score(constrained_answer, chunk_contents)
        if new_score > score:
            state["answer"] = constrained_answer
            state["verified"] = new_score >= GROUNDING_THRESHOLD

    # Persist to session memory
    await append_session_memory(UUID(state["session_id"]), "user", state["query"])
    await append_session_memory(UUID(state["session_id"]), "assistant", state["answer"])
    return state


# ── Step 7: Build citations ───────────────────────────────────────────────────

async def build_output(state: AgentState) -> AgentState:
    """Attach citations with relevance scores."""
    state["citations"] = [
        {
            "chunk_id": str(c.get("id", "")),
            "document_id": str(c.get("payload", {}).get("document_id", "")),
            "filename": c.get("payload", {}).get("filename", ""),
            "page_number": c.get("payload", {}).get("page_number"),
            "chunk_type": c.get("payload", {}).get("chunk_type", "text"),
            "excerpt": str(c.get("payload", {}).get("content", ""))[:200],
            "relevance_score": round(c.get("score", 0.0), 4),
        }
        for c in state["reranked_chunks"]
    ]
    return state


# ── Graph construction ─────────────────────────────────────────────────────────

def build_agent_graph() -> Any:
    builder: StateGraph = StateGraph(AgentState)  # type: ignore[type-arg]
    builder.add_node("decompose", decompose)
    builder.add_node("retrieval", retrieval)
    builder.add_node("reranking", reranking)
    builder.add_node("synthesis", synthesis)
    builder.add_node("generation", generation)
    builder.add_node("self_verify", self_verify)
    builder.add_node("build_output", build_output)

    builder.set_entry_point("decompose")
    builder.add_edge("decompose", "retrieval")
    builder.add_edge("retrieval", "reranking")
    builder.add_edge("reranking", "synthesis")
    builder.add_edge("synthesis", "generation")
    builder.add_edge("generation", "self_verify")
    builder.add_edge("self_verify", "build_output")
    builder.add_edge("build_output", END)

    return builder.compile()


rag_graph = build_agent_graph()
