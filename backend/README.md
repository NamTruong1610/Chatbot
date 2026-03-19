# Agent Backend

A domain-specific AI chatbot backend designed as a website plugin. Businesses embed a single script tag into their website, and the chatbot guides their visitors through business-specific workflows using RAG (Retrieval-Augmented Generation) combined with a rule-based NLP layer.

---

## How It Works

A business pastes one script tag into their website:

```html
<script src="cdn.yourdomain.com/agent.js" data-domain="catering-xyz"></script>
```

The plugin identifies the business via `domain_id`, retrieves that business's documents from the vector database, and uses an LLM to generate responses grounded in the business's actual workflows — not generic internet knowledge.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Python + FastAPI |
| LLM | Ollama (llama3.2) / OpenAI GPT-4o |
| Vector Database | Qdrant |
| Session Store | Redis |
| Persistent Store | PostgreSQL (planned) |
| Embedding Model | all-MiniLM-L6-v2 (HuggingFace) |
| Document Parsing | unstructured |
| Text Splitting | langchain-text-splitters |

---

## Project Structure

```
backend/
├── app/
│   ├── main.py                      # FastAPI entry point, lifespan, middleware, routes
│   ├── routes/                      # URL definitions only
│   │   ├── chat_routes.py
│   │   ├── ingest_routes.py
│   │   └── admin_routes.py
│   ├── controllers/                 # Request/response handling
│   │   ├── chat_controller.py
│   │   ├── ingest_controller.py
│   │   └── admin_controller.py
│   ├── services/                    # Business logic
│   │   ├── chat_service.py          # Orchestrates NLP → RAG → LLM pipeline
│   │   ├── rag_service.py           # Embedding + Qdrant vector search
│   │   ├── ingestion_service.py     # Document parsing, chunking, storing
│   │   ├── session_service.py       # Redis chat history management
│   │   └── summary_service.py       # AI summarisation of ended sessions
│   ├── middlewares/
│   │   ├── auth_middleware.py       # API key validation for protected routes
│   │   ├── error_middleware.py      # Global error handling
│   │   └── logging_middleware.py    # Request/response logging
│   ├── schemas/                     # Pydantic request/response validation
│   │   ├── chat_schema.py
│   │   ├── ingest_schema.py
│   │   └── admin_schema.py
│   ├── models/                      # Database model definitions
│   │   ├── domain_model.py          # Business domain structure
│   │   └── user_summary_model.py    # User session summary structure
│   ├── config/
│   │   └── config.py                # Centralised environment config (pydantic-settings)
│   └── utils/
│       ├── file_parser.py           # PDF, DOCX, TXT, JSON, HTML extraction
│       ├── chunker.py               # Text chunking for RAG ingestion
│       └── uuid_helper.py           # UUID generation for chunk and session IDs
├── data/
│   └── uploads/                     # Temporary file storage during ingestion
├── tests/
├── .env                             # Environment variables (never commit this)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Prerequisites

- Python 3.11+
- Docker Desktop (for Qdrant and Redis)
- Ollama (for local LLM) or an OpenAI API key

---

## Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd backend
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Mac/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the root directory:

```env
# LLM
OPENAI_API_KEY=sk-...          # Required if using OpenAI

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=business_domains

# Redis
REDIS_URL=redis://localhost:6379
SESSION_TTL_SECONDS=3600

# PostgreSQL (planned)
POSTGRES_URL=postgresql://user:password@localhost:5432/agentdb

# App
APP_ENV=development
ADMIN_API_KEY=your-secret-key-here

# Chunking
CHUNK_SIZE=400
CHUNK_OVERLAP=50

# LLM
LLM_MODEL=llama3.2
LLM_MAX_TOKENS=1000
LLM_TEMPERATURE=0.7

# Embedding
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_TOP_K=5
```

### 5. Start Qdrant and Redis with Docker

```bash
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant
docker run -d --name redis  -p 6379:6379 redis
```

### 6. Set up Ollama (local LLM)

```bash
# Install Ollama
brew install ollama

# Start Ollama server
ollama serve

# Pull the model (in a new terminal tab)
ollama pull llama3.2
```

Alternatively, set `LLM_MODEL=gpt-4o` in `.env` and provide a valid `OPENAI_API_KEY` to use OpenAI instead.

### 7. Start the server

```bash
uvicorn app.main:app --reload
```

The server starts at `http://localhost:8000`. The Qdrant collection is created automatically on first startup.

---

## API Endpoints

### Public (no authentication required)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `POST` | `/api/chat/message` | Send a chat message, receive a reply |
| `POST` | `/api/chat/end-session` | End session and trigger AI summarisation |

### Protected (requires `X-API-Key` header)

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/ingest/upload` | Upload a document to the RAG layer |
| `POST` | `/api/ingest/update` | Replace an existing document |
| `DELETE` | `/api/ingest/delete` | Delete a specific document |
| `DELETE` | `/api/ingest/domain` | Wipe all documents for a business domain |
| `GET` | `/api/ingest/documents` | List all documents for a domain |

---

## Testing the API

Interactive docs are available at:
```
http://localhost:8000/docs
```

### Example: Upload a document

```bash
curl -X POST http://localhost:8000/api/ingest/upload \
  -H "X-API-Key: your-admin-key" \
  -F "domain_id=catering-xyz" \
  -F "file=@/path/to/document.txt"
```

### Example: Send a chat message

```bash
curl -X POST http://localhost:8000/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are your vegetarian options?",
    "domain_id": "catering-xyz",
    "user_id": "uuid-test-001",
    "session_id": "sess-test-001"
  }'
```

---

## Architecture Overview

```
HOST WEBSITE
  <script data-domain="catering-xyz">
          │
          ▼
  BROWSER PLUGIN (agent.js)
  Generates user_id (localStorage) + session_id (sessionStorage)
          │
          ▼
  API GATEWAY (FastAPI)
  Middleware: CORS → Logging → Error → Auth
          │
          ├── POST /api/chat/message
          │         │
          │    NLP Layer (rule-based, fast)
          │         │ no match
          │    RAG Service (Qdrant, filtered by domain_id)
          │         │ retrieved chunks
          │    LLM (Ollama / OpenAI)
          │         │
          │    Redis (session history)
          │
          └── POST /api/ingest/upload
                    │
               Parse (unstructured)
                    │
               Chunk (RecursiveCharacterTextSplitter)
                    │
               Embed + Store (Qdrant, tagged with domain_id)
```

### RAG Multi-Tenancy

All businesses share one Qdrant collection (`business_domains`). Each chunk is tagged with `domain_id` and every search filters strictly by that ID — ensuring no cross-business data leakage.

---

## Supported Document Formats

| Format | Parser |
|---|---|
| `.pdf` | unstructured |
| `.docx` | unstructured |
| `.txt` | native Python |
| `.json` | native Python |
| `.html` | BeautifulSoup |

---

## Known Limitations / Roadmap

- [ ] PostgreSQL integration for persistent user summaries
- [ ] Admin controller and dashboard endpoints
- [ ] Browser plugin frontend (`agent.js`)
- [ ] ADMIN_API_KEY validation (currently disabled in development)
- [ ] Fine-tuning pipeline for domain-specific model behaviour
- [ ] Web crawler for automated business data ingestion
- [ ] Production deployment configuration

---

## Development Notes

- The Qdrant collection `business_domains` is created automatically on server startup if it does not exist
- Uploaded files are saved temporarily to `data/uploads/` and deleted immediately after ingestion
- Session history is stored in Redis with a 1-hour TTL — expiry triggers an AI summarisation job
- The NLP layer runs before every RAG call — matched intents return instantly without hitting the LLM
- Error middleware currently returns raw error messages for debugging — revert before production

---

## Environment Variables Reference

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | — | OpenAI API key (required for OpenAI LLM) |
| `QDRANT_HOST` | `localhost` | Qdrant host |
| `QDRANT_PORT` | `6333` | Qdrant port |
| `QDRANT_COLLECTION` | `business_domains` | Qdrant collection name |
| `REDIS_URL` | `redis://localhost:6379` | Redis connection URL |
| `SESSION_TTL_SECONDS` | `3600` | Session expiry in seconds |
| `POSTGRES_URL` | — | PostgreSQL connection URL |
| `ADMIN_API_KEY` | — | API key for protected endpoints |
| `LLM_MODEL` | `llama3.2` | LLM model name |
| `LLM_MAX_TOKENS` | `1000` | Max tokens per LLM response |
| `LLM_TEMPERATURE` | `0.7` | LLM temperature (0 = deterministic) |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | HuggingFace embedding model |
| `EMBEDDING_TOP_K` | `5` | Number of chunks retrieved per query |
| `CHUNK_SIZE` | `400` | Token size per chunk |
| `CHUNK_OVERLAP` | `50` | Overlap between chunks |
| `UPLOAD_DIR` | `data/uploads` | Temp directory for uploaded files |
| `APP_ENV` | `development` | Environment (`development`/`production`) |
