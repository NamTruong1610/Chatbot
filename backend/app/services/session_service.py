# app/services/session_service.py
import redis.asyncio as redis
import json
from sqlalchemy import select
from app.config.config import settings
from app.database import AsyncSessionLocal
from app.models.user_summary_model import UserSummary

class SessionService:
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL)

    async def get_history(self, session_id: str) -> list:
        raw = await self.redis.get(f"session:{session_id}")
        return json.loads(raw) if raw else []

    async def append(self, session_id: str, user_msg: str, bot_reply: str):
        history = await self.get_history(session_id)
        history.append({"role": "user",      "content": user_msg})
        history.append({"role": "assistant", "content": bot_reply})
        # Reset TTL to 1 hour on every new message
        await self.redis.setex(f"session:{session_id}", 3600, json.dumps(history))

    async def get_summary(self, user_id: str, domain_id: str) -> str:
        # Read from PostgreSQL
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(UserSummary).where(
                    UserSummary.user_id == user_id,
                    UserSummary.domain_id == domain_id
                )
            )
            record = result.scalar_one_or_none()
            return record.summary if record else ""
    
    async def delete(self, session_id: str):
        await self.redis.delete(f"session:{session_id}")