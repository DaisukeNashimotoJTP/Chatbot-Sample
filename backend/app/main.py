"""
Main FastAPI application module.
"""
import structlog
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import settings
from app.core.database import init_db, close_db
from app.core.middleware import error_handler_middleware, request_logging_middleware

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting up Chat Service API", version=settings.APP_VERSION)
    await init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Chat Service API")
    await close_db()
    logger.info("Database connections closed")


def create_application() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="A Slack-like real-time chat service API",
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        docs_url=f"{settings.API_V1_PREFIX}/docs",
        redoc_url=f"{settings.API_V1_PREFIX}/redoc",
        lifespan=lifespan,
        debug=settings.DEBUG,
    )
    
    # Add middleware
    setup_middleware(app)
    
    # Include routers
    setup_routers(app)
    
    return app


def setup_middleware(app: FastAPI) -> None:
    """Set up application middleware."""
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )
    
    # Trusted host middleware (for production)
    if not settings.DEBUG:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]  # Configure appropriately for production
        )
    
    # Custom middleware
    app.middleware("http")(request_logging_middleware)
    app.middleware("http")(error_handler_middleware)


def setup_routers(app: FastAPI) -> None:
    """Set up application routers."""
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION
        }
    
    # API v1 routes
    from app.api.v1 import auth, users, workspaces, channels, messages
    from app.websocket import endpoints as websocket_endpoints
    
    app.include_router(
        auth.router,
        prefix=f"{settings.API_V1_PREFIX}/auth",
        tags=["Authentication"]
    )
    app.include_router(
        users.router,
        prefix=f"{settings.API_V1_PREFIX}/users",
        tags=["Users"]
    )
    app.include_router(
        workspaces.router,
        prefix=f"{settings.API_V1_PREFIX}/workspaces",
        tags=["Workspaces"]
    )
    app.include_router(
        channels.router,
        prefix=f"{settings.API_V1_PREFIX}/channels",
        tags=["Channels"]
    )
    app.include_router(
        messages.router,
        prefix=f"{settings.API_V1_PREFIX}",
        tags=["Messages"]
    )
    app.include_router(
        websocket_endpoints.router,
        prefix=f"{settings.API_V1_PREFIX}",
        tags=["WebSocket"]
    )


# Create application instance
app = create_application()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )