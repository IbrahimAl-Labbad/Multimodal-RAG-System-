# Multimodal RAG System

A production-ready, 100% open-source Multimodal Retrieval-Augmented Generation (RAG) system supporting Chat with PDF, Chat with Images, OCR extraction, multimodal embeddings, hybrid vector search via Qdrant, agentic orchestration via LangGraph, streaming answers (SSE), and citations with relevance scoring.

---

## Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI |
| Agent | LangGraph |
| LLM Inference | Ollama (`MODEL_NAME` env) |
| Vision Understanding | LLaVA via Ollama (`VISION_MODEL` env) |
| Multimodal Embeddings | SigLIP / CLIP (HuggingFace) |
| Text Embeddings | SentenceTransformers (`EMBEDDING_MODEL` env) |
| Vector Store | Qdrant |
| Database | PostgreSQL (async SQLAlchemy) |
| Cache | Redis |
| Queue | Celery + RabbitMQ |
| Observability | OpenTelemetry |
| Auth | JWT (python-jose) |
| Frontend | Next.js 14, TailwindCSS, Zustand, SSE |
| CI/CD | GitHub Actions |
| Containers | Docker + Docker Compose |

---

## Quick Start

### 1. Clone & Configure

```bash
git clone <repo-url>
cd multimodal-rag
cp .env.example .env
# Edit .env and fill in all required values
```

### 2. Run with Docker Compose

```bash
docker compose up --build
```

All 8 services will start: `backend`, `frontend`, `worker`, `qdrant`, `postgres`, `redis`, `rabbitmq`, `ollama`.

The backend API is available at `http://localhost:8000`.  
The frontend is available at `http://localhost:3000`.

### 3. Pull Required Ollama Models

After the Ollama container is running:

```bash
docker compose exec ollama ollama pull llama3.1:8b
docker compose exec ollama ollama pull llava:13b
```

---

## Environment Variables

All configuration is driven by environment variables. Copy `.env.example` to `.env` and fill in values.

| Variable | Description | Default |
|---|---|---|
| `OLLAMA_BASE_URL` | Ollama server URL | `http://ollama:11434` |
| `MODEL_NAME` | LLM model for generation | `llama3.1:8b` |
| `VISION_MODEL` | Vision model for image understanding (LLaVA) | `llava:13b` |
| `EMBEDDING_MODEL` | HuggingFace sentence-transformers model | `sentence-transformers/all-MiniLM-L6-v2` |
| `CLIP_MODEL` | CLIP/SigLIP model for multimodal embeddings | `openai/clip-vit-base-patch32` |
| `QDRANT_HOST` | Qdrant host | `qdrant` |
| `QDRANT_PORT` | Qdrant port | `6333` |
| `QDRANT_COLLECTION` | Qdrant collection name | `multimodal_rag` |
| `POSTGRES_URL` | Async PostgreSQL DSN | — |
| `REDIS_URL` | Redis DSN | `redis://redis:6379` |
| `RABBITMQ_URL` | RabbitMQ AMQP URL | — |
| `JWT_SECRET_KEY` | Secret for JWT signing | — |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `JWT_EXPIRE_MINUTES` | Token expiry | `60` |
| `MAX_UPLOAD_SIZE_MB` | Max file upload size | `50` |
| `ALLOWED_EXTENSIONS` | Comma-separated allowed extensions | `pdf,jpg,jpeg,png,webp` |
| `RATE_LIMIT_PER_MINUTE` | API rate limit | `60` |
| `ENABLE_CHAIN_OF_THOUGHT` | Enable hidden CoT reasoning | `false` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OpenTelemetry collector endpoint | — |

### Swapping Models

Change only `.env` — no code changes required:

```bash
MODEL_NAME=qwen2.5:14b       # swap text LLM
VISION_MODEL=llava:7b         # swap vision LLM
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2  # swap embeddings
```

---

## Running Locally (without Docker)

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Workers

```bash
cd backend
celery -A workers.celery_app worker --loglevel=info
```

---

## API Reference

All endpoints are versioned under `/api/v1/` and require a `Bearer` JWT token (except `/health`).

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/upload` | Upload PDF or image |
| `POST` | `/api/v1/index` | Trigger ingestion + indexing |
| `POST` | `/api/v1/chat` | Chat (SSE streaming response) |
| `GET` | `/api/v1/health` | Health check |
| `GET` | `/api/v1/metrics` | OpenTelemetry metrics |

---

## Running Tests

```bash
cd backend
pytest tests/ --cov=. --cov-report=term-missing
```

Target: ≥ 80% coverage.

---

## Running Evaluation (RAGAS)

```bash
python scripts/eval_retrieval.py
```

Benchmark targets:

| Metric | Target |
|---|---|
| Retrieval Recall@5 | ≥ 85% |
| RAGAS Faithfulness | ≥ 0.85 |
| RAGAS Answer Relevance | ≥ 0.80 |
| RAGAS Context Recall | ≥ 0.80 |
| End-to-end latency P95 | < 3 seconds |
| Indexing throughput | ≥ 10 pages/second |

---

## CI/CD

GitHub Actions workflows run automatically on push:

1. `lint.yml` — ruff, mypy, eslint
2. `test.yml` — pytest unit + integration (requires lint to pass)
3. `build.yml` — Docker image builds (requires tests to pass)
4. `deploy.yml` — Deploy to environment (requires build to pass)

Configure secrets in GitHub → Settings → Secrets.
