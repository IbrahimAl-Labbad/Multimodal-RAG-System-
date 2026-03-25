from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestSettings:
    def test_allowed_extensions_set(self):
        from config import Settings
        s = Settings(
            allowed_extensions="pdf,jpg,jpeg",
            jwt_secret_key="test",
        )
        assert s.allowed_extensions_set == {"pdf", "jpg", "jpeg"}

    def test_max_upload_size_bytes(self):
        from config import Settings
        s = Settings(max_upload_size_mb=10, jwt_secret_key="test")
        assert s.max_upload_size_bytes == 10 * 1024 * 1024

    def test_no_hardcoded_model_names(self):
        """Verify model names are configurable via env — not hardcoded."""
        from config import Settings
        s = Settings(model_name="custom-model:7b", jwt_secret_key="test")
        assert s.model_name == "custom-model:7b"


class TestJWT:
    def test_create_and_decode_token(self):
        import os
        os.environ["JWT_SECRET_KEY"] = "test-secret"
        from auth.jwt import create_access_token, decode_access_token
        token = create_access_token("user123")
        payload = decode_access_token(token)
        assert payload["sub"] == "user123"

    def test_invalid_token_raises(self):
        import os
        os.environ["JWT_SECRET_KEY"] = "test-secret"
        from auth.jwt import decode_access_token, CREDENTIALS_EXCEPTION
        from fastapi import HTTPException
        with pytest.raises(HTTPException):
            decode_access_token("invalid.token.here")


class TestQueryClassification:
    def test_text_query(self):
        from pipelines.retrieval import classify_query
        from schemas.query import QueryType
        result = classify_query("What is the summary of chapter 3?")
        assert result == QueryType.TEXT

    def test_image_query(self):
        from pipelines.retrieval import classify_query
        from schemas.query import QueryType
        result = classify_query("Show me the chart in the document")
        assert result == QueryType.MIXED or result == QueryType.IMAGE

    def test_pure_image_query(self):
        from pipelines.retrieval import classify_query
        from schemas.query import QueryType
        result = classify_query("image photo picture visual diagram")
        assert result == QueryType.IMAGE


class TestDocumentSchemas:
    def test_text_chunk_schema(self):
        from schemas.document import TextChunk, DocumentMetadata, ChunkType
        meta = DocumentMetadata(filename="test.pdf", chunk_type=ChunkType.TEXT)
        chunk = TextChunk(content="Hello world", metadata=meta)
        assert chunk.content == "Hello world"
        assert chunk.metadata.chunk_type == ChunkType.TEXT

    def test_ingestion_result_schema(self):
        from schemas.document import IngestionResult
        import uuid
        result = IngestionResult(
            document_id=uuid.uuid4(),
            filename="test.pdf",
            text_chunks=5,
            image_chunks=2,
            table_chunks=1,
            total_chunks=8,
        )
        assert result.total_chunks == 8


class TestCrossEncoderReranker:
    def test_reranker_sorts_by_score(self):
        from agents.tools.cross_encoder_reranker import run_cross_encoder_reranker
        chunks = [
            {"id": "1", "score": 0.3, "payload": {"content": "LangGraph is an agent framework by LangChain."}},
            {"id": "2", "score": 0.6, "payload": {"content": "Qdrant is a vector database."}},
        ]
        with patch("agents.tools.cross_encoder_reranker.get_cross_encoder") as mock_ce:
            import numpy as np
            mock_ce.return_value.predict.return_value = np.array([0.2, 0.8])
            result = run_cross_encoder_reranker("What is Qdrant?", chunks, top_k=2)
        assert result[0]["score"] >= result[-1]["score"]
