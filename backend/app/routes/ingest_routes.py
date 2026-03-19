from fastapi import APIRouter
from app.controllers.ingest_controller import upload_document, update_document, delete_document, delete_domain, list_documents

router = APIRouter()

router.post("/upload")(upload_document)
router.post("/update")(update_document)
router.delete("/delete")(delete_document)
router.delete("/domain")(delete_domain)
router.get("/documents")(list_documents)