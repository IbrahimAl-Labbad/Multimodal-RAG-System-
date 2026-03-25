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

async def self_verify(state: AgentState) -> AgentState:
    """
    Lightweight grounding check: verify key phrases in the answer appear in context.
    In production this can be replaced with an NLI or LLM-as-judge call.
    """
    answer = state.get("answer", "")
    context = state.get("context", "")
    # Basic check: at least 30% of answer sentences reference context content
    sentences = [s.strip() for s in answer.split(".") if len(s.strip()) > 10]
    grounded = sum(1 for s in sentences if any(w in context for w in s.split() if len(w) > 4))
    state["verified"] = (grounded / max(len(sentences), 1)) >= 0.3

    # Persist to session memory
    await append_session_memory(UUID(state["session_id"]), "user", state["query"])
    await append_session_memory(UUID(state["session_id"]), "assistant", answer)
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
