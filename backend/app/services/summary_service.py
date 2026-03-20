from openai import AsyncOpenAI
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.user_summary_model import UserSummary

class SummaryService:
    def __init__(self):
        self.llm = AsyncOpenAI(
            api_key="ollama",
            base_url="http://localhost:11434/v1"
        )

    async def summarise_and_save(self, user_id: str, domain_id: str, history: list):
        if not history:
            return

        # Step 1 — Ask LLM to summarise the conversation
        response = await self.llm.chat.completions.create(
            model="llama3.2",    # ← changed from gpt-4o
            messages=[
                {"role": "system", "content":
                    "Summarise this conversation in 2-3 sentences. Focus on what the user wants, decisions made, and any unresolved questions."},
                {"role": "user", "content": str(history)}
            ]
        )
        summary = response.choices[0].message.content
        
        # Step 2 — Upsert into PostgreSQL
        async with AsyncSessionLocal() as db:
            # Check if a record already exists for this user + domain
            result = await db.execute(
                select(UserSummary).where(
                    UserSummary.user_id == user_id,
                    UserSummary.domain_id == domain_id
                )
            )
            existing = result.scalar_one_or_none()

            if existing:
                # Update existing record
                existing.summary       = summary
                existing.session_count = existing.session_count + 1
            else:
                # Insert new record
                db.add(UserSummary(
                    user_id=user_id,
                    domain_id=domain_id,
                    summary=summary,
                    session_count=1
                ))

            await db.commit()
            print(f"✓ Summary saved for user {user_id} on domain {domain_id}")