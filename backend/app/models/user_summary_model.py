from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base

class UserSummary(Base):
    __tablename__ = "user_summaries"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    user_id       = Column(String,  nullable=False)
    domain_id     = Column(String,  nullable=False)
    summary       = Column(Text,    nullable=True)
    last_seen     = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    session_count = Column(Integer, default=1)

    __table_args__ = (
        # Enforce one row per user per domain
        {"schema": None},
    )
