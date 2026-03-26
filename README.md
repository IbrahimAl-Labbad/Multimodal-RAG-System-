# 🧠 Multimodal RAG System

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB.svg)](https://python.org)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://docs.docker.com/compose/)

A production-ready, **100% open-source** Multimodal Retrieval-Augmented Generation system. Upload PDFs and images, ask questions in natural language, and receive grounded, citation-backed answers — all running on local LLMs with zero cloud dependency.

---

## ✨ Key Features

- **Chat with PDFs** — parse text, tables, and embedded images from any PDF
- **Chat with Images** — visual question answering powered by LLaVA
- **OCR Extraction** — PaddleOCR with automatic Tesseract fallback for scanned documents
- **Multimodal Embeddings** — CLIP for vision, SentenceTransformers for text
- **Hybrid Vector Search** — Qdrant with metadata filtering and cross-encoder reranking
- **Agentic Reasoning** — LangGraph orchestrates a 7-step reasoning pipeline
- **Streaming Answers** — Server-Sent Events for real-time token streaming
- **Grounded Citations** — every answer includes ranked source citations with relevance scores
- **Self-Verification** — answers are checked against retrieved context to prevent hallucination
- **Fully Local** — all inference runs through Ollama; swap models with a single env var change

---

## 🏗️ Architecture

```
┌────────────────┐     ┌─────────────────────────────────────────────────┐
│   Next.js 14   │────▶│              FastAPI Backend                    │
│   Frontend     │ SSE │                                                 │
│                │◀────│  ┌──────────┐  ┌───────────┐  ┌─────────────┐  │
│  • Chat UI     │     │  │ LangGraph│  │ Ingestion │  │ Generation  │  │
│  • File Upload │     │  │  Agent   │──│ Pipeline  │──│  Pipeline   │  │
│  • Citations   │     │  └────┬─────┘  └─────┬─────┘  └──────┬──────┘  │
│  • Dark Mode   │     │       │              │               │         │
└────────────────┘     │  ┌────▼─────┐  ┌─────▼─────┐  ┌─────▼──────┐  │
                       │  │  Qdrant  │  │  Ollama   │  │ PostgreSQL │  │
                       │  │ Vectors  │  │ LLM + VLM │  │  Sessions  │  │
                       │  └──────────┘  └───────────┘  └────────────┘  │
                       │       ┌──────────┐  ┌───────────┐             │
                       │       │  Redis   │  │ RabbitMQ  │             │
                       │       │  Cache   │  │   Queue   │             │
                       │       └──────────┘  └───────────┘             │
                       └─────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

### Backend

| Layer | Technology |
|---|---|
| API Framework | FastAPI |
| Agent Orchestration | LangGraph |
| Schema Validation | Pydantic v2 |
| Async Task Queue | Celery + RabbitMQ |
| Cache & Sessions | Redis |
| Observability | OpenTelemetry |
| ORM | SQLAlchemy (async) |
| Database | PostgreSQL |
| Authentication | JWT via python-jose |

### AI & ML

| Role | Technology |
|---|---|
| LLM Inference | Ollama (local) |
| Text Generation | Llama 3.1, Mistral, Qwen 2.5, Phi-3 |
| Image Understanding | LLaVA (captioning + VQA) |
| Multimodal Embeddings | CLIP / SigLIP (HuggingFace) |
| Text Embeddings | SentenceTransformers |
| PDF Parsing | Unstructured + PyMuPDF |
| OCR | PaddleOCR + Tesseract |
| Reranking | Cross-Encoder (ms-marco-MiniLM) |
| Evaluation | RAGAS |

> **Model separation:** CLIP/SigLIP handles **embeddings only** (image↔text similarity). LLaVA handles **image understanding only** (captioning, VQA). These models are not interchangeable.

### Frontend

| Layer | Technology |
|---|---|
| Framework | Next.js 14 (App Router) |
| Styling | TailwindCSS |
| Realtime Streaming | Server-Sent Events |
| State Management | Zustand |

### Infrastructure

| Layer | Technology |
|---|---|
| Containers | Docker + Docker Compose |
| CI/CD | GitHub Actions |
| Vector Store | Qdrant |

---

## 🚀 Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) & Docker Compose v2+
- (Optional) NVIDIA GPU + [nvidia-container-toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) for GPU-accelerated inference

### 1. Clone & Configure

```bash
git clone https://github.com/IbrahimAl-Labbad/Multimodal-RAG-System-.git
cd Multimodal-RAG-System-
cp .env.example .env
```

Open `.env` and set `JWT_SECRET_KEY` — generate one with:

```bash
openssl rand -hex 32
```

### 2. Start All Services

```bash
docker compose up --build
```

This launches 8 services: **backend**, **frontend**, **worker**, **qdrant**, **postgres**, **redis**, **rabbitmq**, and **ollama**.

### 3. Pull the AI Models

After the Ollama container is running:

```bash
docker compose exec ollama ollama pull llama3.1:8b
docker compose exec ollama ollama pull llava:13b
```

### 4. Open the App

| Service | URL |
|---|---|
| Frontend | [http://localhost:3000](http://localhost:3000) |
| Backend API | [http://localhost:8000](http://localhost:8000) |
| API Docs | [http://localhost:8000/docs](http://localhost:8000/docs) |
| RabbitMQ Dashboard | [http://localhost:15672](http://localhost:15672) |

---

## ⚙️ Configuration

All configuration is controlled through environment variables — **no model names, URLs, or secrets are hardcoded anywhere in the codebase**. Changing a model or endpoint requires only editing `.env`.

Copy `.env.example` to `.env` and customize as needed:

### LLM & Vision Models

| Variable | Description | Default |
|---|---|---|
| `OLLAMA_BASE_URL` | Ollama server endpoint | `http://ollama:11434` |
| `MODEL_NAME` | Text generation model | `llama3.1:8b` |
| `VISION_MODEL` | Image understanding model (LLaVA) | `llava:13b` |

### Embeddings

| Variable | Description | Default |
|---|---|---|
| `EMBEDDING_MODEL` | SentenceTransformers text embedding model | `sentence-transformers/all-MiniLM-L6-v2` |
| `CLIP_MODEL` | CLIP/SigLIP multimodal embedding model | `openai/clip-vit-base-patch32` |

### Vector Store

| Variable | Description | Default |
|---|---|---|
| `QDRANT_HOST` | Qdrant hostname | `qdrant` |
| `QDRANT_PORT` | Qdrant port | `6333` |
| `QDRANT_COLLECTION` | Collection name | `multimodal_rag` |

### Database & Services

| Variable | Description | Default |
|---|---|---|
| `POSTGRES_URL` | Async PostgreSQL DSN | `postgresql+asyncpg://user:password@postgres:5432/ragdb` |
| `REDIS_URL` | Redis connection string | `redis://redis:6379` |
| `RABBITMQ_URL` | RabbitMQ AMQP endpoint | `amqp://user:password@rabbitmq:5672/` |

### Authentication

| Variable | Description | Default |
|---|---|---|
| `JWT_SECRET_KEY` | **Required** — secret for signing tokens | *(empty — must be set)* |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` |
| `JWT_EXPIRE_MINUTES` | Token expiry in minutes | `60` |

### Upload & Rate Limiting

| Variable | Description | Default |
|---|---|---|
| `MAX_UPLOAD_SIZE_MB` | Maximum file upload size | `50` |
| `ALLOWED_EXTENSIONS` | Comma-separated allowed file types | `pdf,jpg,jpeg,png,webp` |
| `RATE_LIMIT_PER_MINUTE` | API rate limit per client | `60` |

### Advanced

| Variable | Description | Default |
|---|---|---|
| `ENABLE_CHAIN_OF_THOUGHT` | Enable hidden internal reasoning | `false` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OpenTelemetry collector | `http://otel-collector:4317` |

---

## 🔄 Swapping Models

Changing models requires **only a `.env` change** — no code modifications:

```bash
# Use a different text LLM
MODEL_NAME=mistral:7b

# Use a smaller vision model (less VRAM)
VISION_MODEL=llava:7b

# Use a stronger embedding model
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2

# Production: use a larger model
MODEL_NAME=llama3.1:70b
```

After changing `.env`, restart the backend:

```bash
docker compose restart backend worker
docker compose exec ollama ollama pull <new-model-name>
```

---

## 🧪 Running Locally (without Docker)

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

### Celery Worker

```bash
cd backend
celery -A workers.celery_app worker --loglevel=info
```

> **Note:** When running outside Docker, update `.env` hostnames from service names (`qdrant`, `postgres`, `redis`, etc.) to `localhost`.

---

## 📡 API Reference

All endpoints are versioned under `/api/v1/` and require a `Bearer` JWT token (except health check).

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/upload` | Upload a PDF or image file |
| `POST` | `/api/v1/index` | Trigger ingestion and indexing pipeline |
| `POST` | `/api/v1/chat` | Chat with documents (SSE streaming response) |
| `GET` | `/api/v1/health` | Health check (no auth required) |
| `GET` | `/api/v1/metrics` | OpenTelemetry metrics |

### Example: Chat Request

```bash
curl -N -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -d '{"query": "What are the key findings in the report?", "top_k": 5}'
```

---

## 🧬 Agent Reasoning Pipeline

The LangGraph agent processes every query through a 7-step reasoning chain:

```
1. Decomposition  → Break complex queries into sub-queries
2. Retrieval      → Vector search in Qdrant (text + multimodal)
3. Reranking      → Cross-encoder scoring and filtering
4. Synthesis      → Assemble context from top chunks
5. Generation     → Stream answer via Ollama
6. Verification   → N-gram grounding check against source chunks
7. Output         → Emit answer with ranked citations
```

If the verification step detects poor grounding (< 30% n-gram overlap with source content), the answer is automatically re-generated with a constrained prompt.

---

## ✅ Testing

```bash
cd backend
pytest tests/ --cov=. --cov-report=term-missing
```

### Test Coverage Targets

| Type | Target |
|---|---|
| Unit Tests | ≥ 80% backend coverage |
| Integration Tests | All 5 API endpoints |
| RAGAS Evaluation | Faithfulness ≥ 0.85, Context Recall ≥ 0.80 |

### Running RAGAS Evaluation

```bash
python scripts/eval_retrieval.py
```

### Benchmark Targets

| Metric | Target |
|---|---|
| Retrieval Recall@5 | ≥ 85% |
| RAGAS Faithfulness | ≥ 0.85 |
| RAGAS Answer Relevance | ≥ 0.80 |
| RAGAS Context Recall | ≥ 0.80 |
| End-to-end P95 Latency | < 3 seconds |
| Indexing Throughput | ≥ 10 pages/second |

---

## 🔁 CI/CD

GitHub Actions workflows run automatically on push:

| Step | Workflow | Depends On |
|---|---|---|
| 1 | **Lint** — ruff, mypy, ESLint | — |
| 2 | **Test** — pytest with PostgreSQL + Redis | Lint ✓ |
| 3 | **Build** — Docker images → GHCR | Test ✓ |
| 4 | **Deploy** — SSH to production server | Build ✓ |

Configure deployment secrets in **GitHub → Settings → Secrets**: `DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_SSH_KEY`.

---

## 📁 Project Structure

```
backend/
├── api/v1/              # FastAPI route handlers
├── agents/              # LangGraph agent graph + tool nodes
│   └── tools/           # pdf_reader, image_analyzer, vector_retriever, etc.
├── pipelines/           # Ingestion, retrieval, generation pipelines
├── models/              # LLM, vision, and embedding wrappers
├── schemas/             # Pydantic v2 request/response models
├── storage/             # Qdrant, PostgreSQL, Redis clients
├── workers/             # Celery app + async tasks
├── observability/       # OpenTelemetry tracing + metrics
├── auth/                # JWT creation, validation, middleware
├── config.py            # Centralized settings (pydantic-settings)
└── main.py              # FastAPI application entry point

frontend/
├── app/                 # Next.js 14 App Router pages
├── components/          # React components (ChatWindow, FileUpload, etc.)
├── hooks/               # Custom hooks (useStream for SSE)
└── store/               # Zustand state management

scripts/                 # Evaluation and ingestion scripts
docker/                  # Dockerfiles (backend, frontend, worker)
tests/                   # Unit, integration, and evaluation tests
.github/workflows/       # CI/CD pipeline definitions
```

---

## 🔒 Security

- All `/api/v1/` endpoints are protected with JWT authentication
- File uploads are validated: type whitelist + configurable size limit
- Input sanitization on all user-supplied text
- No secrets, tokens, or model names are hardcoded — everything is read from environment variables
- `.env` is gitignored; `.env.example` provides the template

---

## 📄 License

This project is open-source. See [LICENSE](LICENSE) for details.
