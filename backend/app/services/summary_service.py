from openai import AsyncOpenAI
from app.config.config import settings

class SummaryService:
    def __init__(self):
        self.llm = AsyncOpenAI(
            api_key="ollama",
            base_url="http://localhost:11434/v1"
        )

    async def summarise_and_save(self, user_id: str, domain_id: str, history: list):
        if not history:
            return

        # Ask LLM to summarise the conversation
        response = await self.llm.chat.completions.create(
            model="llama3.2",    # ← changed from gpt-4o
            messages=[
                {"role": "system", "content":
                    "Summarise this conversation in 2-3 sentences. Focus on what the user wants, decisions made, and any unresolved questions."},
                {"role": "user", "content": str(history)}
            ]
        )
        summary = response.choices[0].message.content