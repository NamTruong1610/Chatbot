# app/services/rag_service.py
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer
from app.config.config import settings

class RAGService:
    def __init__(self):
        self.client = QdrantClient(settings.QDRANT_HOST, port=settings.QDRANT_PORT)
        self.embedder = SentenceTransformer(settings.EMBEDDING_MODEL)

    async def retrieve(self, query: str, domain_id: str) -> list[str]:
        # Embed the user's question
        query_vector = self.embedder.encode(query).tolist()

        # Search Qdrant — ONLY within this business's documents
        # "business_domains" is the name of the collection in Qdrant — like a table name in SQL or a collection name in MongoDB. It holds every chunk from every business, all in one place, separated by domain_id. For example:
        
        # id: "catering-xyz_doc1_chunk_0"                                
        # vector: [0.231, -0.847, 0.103, ...]                            
        # payload: {                                                     
        #     "text": "Step 1: Fill out the booking form...",            
        #     "domain_id": "catering-xyz",                               
        #     "document_id": "doc1",                                     
        #     "filename": "booking_process.pdf"                          
        # }  
          
        results = self.client.query_points(
            collection_name=settings.QDRANT_COLLECTION,
            query=query_vector,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="domain_id",
                        match=MatchValue(value=domain_id)
                    )
                ]
            ),
            limit=settings.EMBEDDING_TOP_K
        )

        # Return just the text chunks
        return [r.payload["text"] for r in results.points]