from pydantic import BaseModel
from datetime import datetime

class DomainCreateRequest(BaseModel):
    business_name: str
    welcome_message: str
    bot_persona: str
    allowed_origins: list[str]

class DomainUpdateRequest(BaseModel):
    welcome_message: str | None = None
    bot_persona: str | None = None
    allowed_origins: list[str] | None = None
    is_active: bool | None = None

class DomainResponse(BaseModel):
    domain_id: str
    business_name: str
    welcome_message: str
    is_active: bool
    created_at: datetime