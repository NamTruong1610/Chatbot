# app/middlewares/logging_middleware.py
import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()

        logger.info(f"→ {request.method} {request.url.path}")

        response = await call_next(request)

        duration = round((time.time() - start) * 1000, 2)
        logger.info(f"← {response.status_code} {request.url.path} ({duration}ms)")

        return response