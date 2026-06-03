import logging

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.exceptions import ServiceError

logger = logging.getLogger(__name__)

class ErrorResponse(BaseModel):
    detail: str
    error_type: str | None = None
    status_code: int

def register_error_handlers(app):
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.error(f"HTTPException: {exc.detail} (status {exc.status_code})")
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                detail=exc.detail,
                error_type=type(exc).__name__,
                status_code=exc.status_code,
            ).dict(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.error(f"Validation error: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                detail="Validation error",
                error_type=type(exc).__name__,
                status_code=422,
            ).dict(),
        )

    @app.exception_handler(ServiceError)
    async def service_error_handler(request: Request, exc: ServiceError):
        logger.error(f"ServiceError: {exc.message} (status {exc.status_code})")
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                detail=exc.message,
                error_type=type(exc).__name__,
                status_code=exc.status_code,
            ).dict(),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception occurred")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                detail="Internal server error",
                error_type=type(exc).__name__,
                status_code=500,
            ).dict(),
        )
