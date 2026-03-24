"""Global error handling via FastAPI exception handlers (Starlette-compatible)."""

import traceback
import uuid

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.utils.logger import logger


def add_exception_handlers(app: FastAPI) -> None:
    """Register application-wide exception handlers on *app*."""

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        logger.warning("ValueError on %s: %s", request.url, exc)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "The requested resource was not found"},
        )

    @app.exception_handler(500)
    async def internal_error_handler(request: Request, exc: Exception) -> JSONResponse:
        error_id = str(uuid.uuid4())
        logger.error("Unhandled error [%s] on %s:\n%s", error_id, request.url, traceback.format_exc())
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error", "error_id": error_id},
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        error_id = str(uuid.uuid4())
        logger.error("Unexpected error [%s] on %s: %s", error_id, request.url, exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred", "error_id": error_id},
        )


# Keep a lightweight sentinel class for import compatibility
class ErrorHandlerMiddleware:
    """No-op marker class; error handling is done via exception handlers."""
    pass
