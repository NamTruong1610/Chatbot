from fastapi import APIRouter
from app.controllers.chat_controller import send_message, end_session

router = APIRouter()

router.post("/message")(send_message)
router.post("/end-session")(end_session)
