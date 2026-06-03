import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.agents import router as agents_router
from app.api.analytics import router as analytics_router
from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.documents import router as documents_router
from app.api.errors import register_error_handlers
from app.api.health import router as health_router
from app.api.query import router as query_router
from app.api.search import router as search_router
from app.core.config import settings
from app.core.logging import configure_logging

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(
        title=settings.project_name,
        version=settings.app_version,
        description="Backend API for the Enterprise Knowledge Assistant.",
    )

    cors_kwargs: dict = {
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    }
    if settings.app_env == "development":
        cors_kwargs["allow_origin_regex"] = r"http://(localhost|127\.0\.0\.1):3000"
        cors_kwargs["allow_origins"] = settings.cors_origins
    else:
        cors_kwargs["allow_origins"] = settings.cors_origins

    app.add_middleware(CORSMiddleware, **cors_kwargs)

    @app.exception_handler(RuntimeError)
    async def handle_runtime_error(_: Request, exc: RuntimeError) -> JSONResponse:
        logger.exception("Unhandled runtime error")
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc)},
        )

    app.include_router(health_router, tags=["health"])
    app.include_router(auth_router)
    app.include_router(documents_router)
    app.include_router(search_router)
    app.include_router(query_router)
    app.include_router(chat_router)
    app.include_router(agents_router)
    app.include_router(analytics_router)
    # Register source citation endpoint
    from app.api.source import router as source_router
    app.include_router(source_router)
    register_error_handlers(app)
    return app



app = create_app()
