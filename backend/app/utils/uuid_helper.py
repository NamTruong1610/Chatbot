# app/utils/uuid_helper.py
import uuid

def generate_id() -> str:
    """Generate a new UUID string."""
    return str(uuid.uuid4())

def generate_chunk_id(domain_id: str, document_id: str, chunk_index: int) -> str:
    """
    Generate a deterministic, readable chunk ID.
    e.g. "catering-xyz_doc1_chunk_0"
    Makes chunks traceable back to their source document.
    """
    return f"{domain_id}_{document_id}_chunk_{chunk_index}"
