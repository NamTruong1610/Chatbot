# app/utils/chunker.py
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config.config import settings

def chunk_text(text: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,       # 400 (from config)
        chunk_overlap=settings.CHUNK_OVERLAP  # 50  (from config)
    )
    chunks = splitter.split_text(text)
    return [c.strip() for c in chunks if c.strip()]  # remove empty chunks