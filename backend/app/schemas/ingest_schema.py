from pydantic import BaseModel
from datetime import datetime

class DeleteDocumentRequest(BaseModel):
    domain_id: str
    document_id: str

class DeleteDomainRequest(BaseModel):
    domain_id: str

class DocumentItem(BaseModel):
    document_id: str
    filename: str
    uploaded_at: datetime

class ListDocumentsResponse(BaseModel):
    domain_id: str
    total: int
    documents: list[DocumentItem]

class IngestResponse(BaseModel):
    status: str
    message: str