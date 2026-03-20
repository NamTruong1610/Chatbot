# app/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config.config import settings

# Convert standard postgres URL to async version
# postgresql://... → postgresql+asyncpg://...
DATABASE_URL = settings.POSTGRES_URL.replace(
    "postgresql://", "postgresql+asyncpg://"
)

# Force TCP connection to Docker, bypasses local Unix socket
if "?" not in DATABASE_URL:
    DATABASE_URL += "?host=localhost"

print(f"DATABASE_URL = {DATABASE_URL}")

engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session