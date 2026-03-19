# app/middlewares/auth_middleware.py
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.config.config import settings

# Routes that don't require an API key (public — end users)
PUBLIC_ROUTES = [
    "/api/chat/message",
    "/api/chat/end-session",
    "/api/health",
    "/",
    "/docs",           # ← FastAPI interactive docs
    "/openapi.json",   # ← FastAPI docs fetches this behind the scenes
    "/redoc",          # ← alternative docs UI
]

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip auth for public routes
        if request.url.path in PUBLIC_ROUTES:
            return await call_next(request)

        # All other routes (ingest, admin) require API key
        api_key = request.headers.get("X-API-Key")

        if not api_key:
            return JSONResponse(
                status_code=401,
                content={"status": "error", "message": "Missing API key"}
            )

        # if api_key != settings.ADMIN_API_KEY:
        #     return JSONResponse(
        #         status_code=403,
        #         content={"status": "error", "message": "Invalid API key"}
        #     )

        return await call_next(request)