# app/middlewares/error_middleware.py
import logging
import traceback
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

class ErrorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            logger.error(f"Unhandled error on {request.url.path}: {str(e)}")
            traceback.print_exc()   # ← prints full traceback to terminal
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": str(e)   # ← shows actual error in response
                }
            )