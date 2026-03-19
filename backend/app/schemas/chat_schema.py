from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    domain_id: str
    user_id: str
    session_id: str

class ChatResponse(BaseModel):
    reply: str
    session_id: str

class EndSessionRequest(BaseModel):
    user_id: str
    domain_id: str
    session_id: str