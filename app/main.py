from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy.exc import SQLAlchemyError

from application.use_cases.seed_admin_user_usecase import SeedAdminUserUseCase
from core.dependencies import get_settings
from core.environment_setting import Settings
from core.logging_config import get_logger
from infrastructure.database.config import get_session
from presentation.api.v1.auth.auth_router import auth_router
from presentation.api.v1.test.test_router import test_router
from presentation.api.v1.users.user_router import user_router
from presentation.middlewares.auth_middleware import AuthMiddleware
from presentation.middlewares.exception_middleware import ExceptionMiddleware
from presentation.middlewares.request_setup_middleware import RequestSetupMiddleware
from presentation.middlewares.security_headers_middleware import (
    SecurityHeadersMiddleware,
)

logger = get_logger(__name__)


def seed_initial_admin(settings: Settings, session_factory=get_session) -> None:
    """Create the initial admin account from env settings if configured and missing."""
    username = (settings.admin_username or "").strip()
    password = (
        settings.admin_password.get_secret_value()
        if settings.admin_password is not None
        else ""
    )
    if not username or not password:
        if username or password:
            logger.warning(
                "Skipping admin account seeding: both ADMIN_USERNAME and ADMIN_PASSWORD must be set."
            )
        return

    try:
        with next(session_factory()) as session:
            user = SeedAdminUserUseCase(session).invoke(username, password)
            if user is not None:
                logger.info("Initial admin account '%s' is ready.", user.username)
    except SQLAlchemyError as exc:
        logger.warning("Skipping admin account seeding due to database error: %s", exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for handling startup and shutdown events.
    Code before yield runs on startup, code after yield runs on shutdown.
    """
    # Startup
    print("Starting up...")
    active_settings: Settings = getattr(app.state, "settings", None) or get_settings()
    seed_initial_admin(active_settings)

    yield  # Application is running

    # Shutdown
    print("Shutting down...")


__MIDDLEWARES__ = [
    RequestSetupMiddleware,
    ExceptionMiddleware,
    AuthMiddleware,
]


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the FastAPI application instance."""
    active_settings = settings or get_settings()
    application = FastAPI(title=active_settings.app_name, lifespan=lifespan)
    application.state.settings = active_settings

    if settings is not None:
        application.dependency_overrides[get_settings] = lambda: active_settings

    # Setting v1 APIs
    v1_router = APIRouter(prefix="/v1", tags=["v1"])
    v1_router.include_router(auth_router, prefix="/auth", tags=["auth"])
    v1_router.include_router(user_router, prefix="/users", tags=["users"])
    v1_router.include_router(test_router, prefix="/test", tags=["test"])

    application.include_router(v1_router, prefix="/api")

    # Add middlewares in innermost -> outermost order
    for middleware in reversed(__MIDDLEWARES__):
        application.add_middleware(middleware)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=active_settings.cors_origins,
        allow_credentials=active_settings.cors_allow_credentials,
        allow_methods=active_settings.cors_allow_methods,
        allow_headers=active_settings.cors_allow_headers,
        max_age=active_settings.cors_max_age,
    )

    application.add_middleware(
        SecurityHeadersMiddleware,
        is_production=(active_settings.env == "production"),
        hsts_max_age=active_settings.hsts_max_age,
    )

    if active_settings.env == "production":
        application.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=active_settings.allowed_hosts,
        )

    return application


app = create_app()
