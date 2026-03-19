# app/controllers/chat_controller.py
from fastapi import Request
from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

chat_service = ChatService()

async def send_message(request: ChatRequest) -> ChatResponse:
    # 1. Unpack the validated request (Pydantic already validated it)
    # 2. Call the service
    # 3. Return the response
    result = await chat_service.process_message(
        message=request.message,
        domain_id=request.domain_id,
        user_id=request.user_id,
        session_id=request.session_id
    )
    return ChatResponse(reply=result["reply"], session_id=result["session_id"])

async def end_session(request: Request):
    body = await request.json()
    await chat_service.close_session(body["user_id"], body["domain_id"], body["session_id"])
    return {"status": "session closed"}

