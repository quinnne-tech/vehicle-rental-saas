"""Global error handler middleware"""

from fastapi import Request
from fastapi.responses import JSONResponse
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


async def error_handler_middleware(request: Request, call_next):
    """Global error handling middleware"""
    try:
        response = await call_next(request)
        return response
    except Exception as exc:
        logger.error(
            f"Error: {str(exc)}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
