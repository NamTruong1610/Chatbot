# app/services/chat_service.py
from app.services.rag_service import RAGService
from app.services.session_service import SessionService
from app.services.summary_service import SummaryService
from app.config.config import settings
from openai import AsyncOpenAI

class ChatService:
    def __init__(self):
        self.rag = RAGService()
        self.session = SessionService()
        self.summary = SummaryService()
        self.llm = AsyncOpenAI(
            api_key="ollama",
            base_url="http://localhost:11434/v1"
        )

    async def process_message(self, message, domain_id, user_id, session_id):

        # Step 1 — Check NLP rules first (fast, predictable) to return a reply welcoming the user (e.g. "Hello, user...")
        nlp_response = self._check_nlp_rules(message)
        if nlp_response:
            await self.session.append(session_id, message, nlp_response)
            return { "reply": nlp_response, "session_id": session_id }

        # Step 2 — Retrieve relevant business context from Qdrant
        context_chunks = await self.rag.retrieve(message, domain_id)

        # Step 3 — Load chat history from Redis
        history = await self.session.get_history(session_id)

        # Step 4 — Load user's past session summary from DB
        summary = await self.session.get_summary(user_id, domain_id)

        # Step 5 — Call LLM with everything assembled
        reply = await self._call_llm(message, context_chunks, history, summary, domain_id)

        # Step 6 — Save the new message + reply to Redis
        await self.session.append(session_id, message, reply)

        return { "reply": reply, "session_id": session_id }

    def _check_nlp_rules(self, message):
        msg = message.lower()
        if any(word in msg for word in ["hello", "hi", "hey"]):
            return "Hi there! How can I help you today?"
        if "opening hours" in msg or "open" in msg:
            return "We're open Monday to Friday, 9am to 5pm."
        return None  # No match — fall through to LLM

    async def _call_llm(self, message, chunks, history, summary, domain_id):
        print(f">>> SUMMARY INJECTED: {summary}") 
        context = "\n".join(chunks)
        system_prompt = f"""You are a booking assistant for domain {domain_id}. 
        Only use the information provided in the Business Context below to answer.
        If the answer is not found in the Business Context, say "I don't have that information, please contact us directly."
        Do NOT use your own knowledge. Do NOT make anything up.

        Business Context:
        {context}

        What we know about this user from past visits:
        {summary if summary else "This is a new user with no previous history."}

        If the user has past visit history, briefly acknowledge it at the start of your response
        before answering their current question.
        """
        messages = [{"role": "system", "content": system_prompt}]
        messages += history  # Previous turns in this session
        messages.append({"role": "user", "content": message})

        response = await self.llm.chat.completions.create(
            model="llama3.2",
            messages=messages
        )
        return response.choices[0].message.content
    
    async def close_session(self, user_id: str, domain_id: str, session_id: str):
        # Step 1 — Get the full history before deleting it
        history = await self.session.get_history(session_id)

        # Step 2 — Summarise and persist to PostgreSQL
        await self.summary.summarise_and_save(user_id, domain_id, history)

        # Step 3 — Delete the session from Redis
        await self.session.delete(session_id)