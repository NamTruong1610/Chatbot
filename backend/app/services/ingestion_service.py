# app/services/ingestion_service.py
from app.utils.file_parser import parse_file
from app.utils.chunker import chunk_text
from app.utils.uuid_helper import generate_id
from app.services.rag_service import RAGService
from datetime import datetime, timezone

class IngestionService:
    def __init__(self):
        self.rag = RAGService()

    async def ingest_document(self, file_path: str, domain_id: str, document_id: str = None):
        # Generate a document_id if not provided
        if not document_id:
            document_id = generate_id()

        # Step 1 — Extract raw text
        raw_text = parse_file(file_path)

        # Step 2 — Split into chunks
        chunks = chunk_text(raw_text)

        # Step 3 — Embed and store each chunk
        points = []
        for i, chunk in enumerate(chunks):
            vector = self.rag.embedder.encode(chunk).tolist()
            points.append({
                "id": generate_id(),        # ← valid UUID now
                "vector": vector,
                "payload": {
                    "text": chunk,
                    "domain_id": domain_id,
                    "document_id": document_id,
                    "chunk_index": i,
                    "filename": file_path.split("/")[-1],
                    "uploaded_at": datetime.now(timezone.utc).isoformat()
                }
            })

        self.rag.client.upsert(
            collection_name="business_domains",
            points=points                   # ← upsert all chunks in one call
        )

        return document_id                  # ← return so controller can track it

    async def update_document(self, file_path: str, domain_id: str, document_id: str):
        # Step 1 — Delete all existing chunks for this document
        await self.delete_document(domain_id, document_id)

        # Step 2 — Re-ingest the corrected file
        await self.ingest_document(file_path, domain_id, document_id)

    async def delete_document(self, domain_id: str, document_id: str):
        self.rag.client.delete(
            collection_name="business_domains",
            points_selector={
                "filter": {
                    "must": [
                        {"key": "domain_id",   "match": {"value": domain_id}},
                        {"key": "document_id", "match": {"value": document_id}}
                    ]
                }
            }
        )
    
    async def delete_domain(self, domain_id: str):
        self.rag.client.delete(
            collection_name="business_domains",
            points_selector={
                "filter": {
                    "must": [
                        {"key": "domain_id", "match": {"value": domain_id}}
                    ]
                }
            }
        )

    async def list_documents(self, domain_id: str) -> list:
        results = self.rag.client.scroll(
            collection_name="business_domains",
            scroll_filter={
                "must": [{"key": "domain_id", "match": {"value": domain_id}}]
            },
            with_payload=True,
            with_vectors=False,   # no need to return the vectors themselves
            limit=1000
        )

        # Extract unique documents from chunks
        seen = set()
        documents = []
        for point in results[0]:
            doc_id = point.payload["document_id"]
            if doc_id not in seen:
                seen.add(doc_id)
                documents.append({
                    "document_id": doc_id,
                    "filename": point.payload["filename"],
                    "uploaded_at": point.payload["uploaded_at"]
                })
        return documents
