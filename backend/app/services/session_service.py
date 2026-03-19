# app/services/session_service.py
import redis.asyncio as redis
import json
from app.config.config import settings

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
        # Fetch from PostgreSQL/MongoDB
        # Returns empty string if first visit
        return ""
    
    async def delete(self, session_id: str):
        await self.redis.delete(f"session:{session_id}")