import os
import uuid
from fastapi import UploadFile, File, Form, HTTPException
from app.services.ingestion_service import IngestionService

ingestion_service = IngestionService()

UPLOAD_DIR = "data/uploads"
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".json", ".html"}

def validate_file(filename: str):
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {ALLOWED_EXTENSIONS}"
        )
    return ext

async def save_upload(file: UploadFile) -> str:
    """Save the uploaded file to disk and return its path."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{file.filename}")
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    return file_path

async def cleanup(file_path: str):
    """Delete the temp file after ingestion."""
    if os.path.exists(file_path):
        os.remove(file_path)

# ── Endpoints ────────────────────────────────────────────────────

async def upload_document(
    domain_id: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Upload a new document and ingest it into the RAG layer.
    Expects multipart/form-data with domain_id and file.
    """
    validate_file(file.filename)
    file_path = await save_upload(file)

    try:
        await ingestion_service.ingest_document(
            file_path=file_path,
            domain_id=domain_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
    finally:
        await cleanup(file_path)  # always delete temp file, even if ingestion fails

    return {
        "status": "success",
        "message": f"'{file.filename}' ingested successfully for domain '{domain_id}'"
    }


async def update_document(
    domain_id: str = Form(...),
    document_id: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Replace an existing document. Deletes old chunks and re-ingests the new file.
    Expects multipart/form-data with domain_id, document_id, and file.
    """
    validate_file(file.filename)
    file_path = await save_upload(file)

    try:
        await ingestion_service.update_document(
            file_path=file_path,
            domain_id=domain_id,
            document_id=document_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")
    finally:
        await cleanup(file_path)

    return {
        "status": "success",
        "message": f"Document '{document_id}' updated successfully for domain '{domain_id}'"
    }


async def delete_document(
    domain_id: str = Form(...),
    document_id: str = Form(...)
):
    """
    Delete all chunks belonging to a specific document within a domain.
    """
    try:
        await ingestion_service.delete_document(
            domain_id=domain_id,
            document_id=document_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

    return {
        "status": "success",
        "message": f"Document '{document_id}' deleted from domain '{domain_id}'"
    }


async def delete_domain(domain_id: str = Form(...)):
    """
    Wipe ALL documents and chunks for an entire business domain.
    Use with caution — this is irreversible.
    """
    try:
        await ingestion_service.delete_domain(domain_id=domain_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Domain delete failed: {str(e)}")

    return {
        "status": "success",
        "message": f"All data for domain '{domain_id}' has been deleted"
    }


async def list_documents(domain_id: str):
    """
    List all documents uploaded for a given domain.
    domain_id is passed as a query parameter: GET /api/ingest/documents?domain_id=catering-xyz
    """
    try:
        documents = await ingestion_service.list_documents(domain_id=domain_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")

    return {
        "domain_id": domain_id,
        "total": len(documents),
        "documents": documents
    }