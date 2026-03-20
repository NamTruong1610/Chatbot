from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import chat_routes, ingest_routes, admin_routes
from app.middlewares.logging_middleware import LoggingMiddleware
from app.middlewares.error_middleware import ErrorMiddleware
from app.middlewares.auth_middleware import AuthMiddleware
from app.config.config import settings
from app.database import engine, Base
from app.models import user_summary_model  
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Runs on startup ──────────────────────────────────────────
    client = QdrantClient(settings.QDRANT_HOST, port=settings.QDRANT_PORT)
    existing = [c.name for c in client.get_collections().collections]

    if settings.QDRANT_COLLECTION not in existing:
        client.create_collection(
            collection_name=settings.QDRANT_COLLECTION,
            vectors_config=VectorParams(
                size=384,
                distance=Distance.COSINE
            )
        )
        print(f"✓ Created collection: {settings.QDRANT_COLLECTION}")
    else:
        print(f"✓ Collection already exists: {settings.QDRANT_COLLECTION}")
        
    # ── PostgreSQL tables ────────────────────────────────────────
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("✓ PostgreSQL tables ready")

    yield  # ← everything above runs on startup, everything below runs on shutdown

    # ── Runs on shutdown ─────────────────────────────────────────
    print("Shutting down...")

app = FastAPI(title="Agent Backend")

# --- Middlewares (runs on every request) ---
app.add_middleware(CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)
app.add_middleware(LoggingMiddleware)
app.add_middleware(ErrorMiddleware)
app.add_middleware(AuthMiddleware)

# --- Mount routes (like app.use('/api/chat', chatRouter) in Express) ---
app.include_router(chat_routes.router,   prefix="/api/chat",   tags=["Chat"])
app.include_router(ingest_routes.router, prefix="/api/ingest", tags=["Ingest"])
# app.include_router(admin_routes.router,  prefix="/api/admin",  tags=["Admin"])


@app.get("/")
def health():
    return {"status": "ok"}
