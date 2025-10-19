from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter

from presentation.api.v1.auth.auth_router import auth_router
from presentation.api.v1.test.test_router import test_router
from presentation.api.v1.users.user_router import user_router
from presentation.middlewares.auth_middleware import AuthMiddleware
from presentation.middlewares.exception_middleware import ExceptionMiddleware
from presentation.middlewares.request_setup_middleware import RequestSetupMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for handling startup and shutdown events.
    Code before yield runs on startup, code after yield runs on shutdown.
    """
    # Startup
    print("Starting up...")
    # Add any initialization logic here:
    # - Database connection pool setup
    # - Cache initialization
    # - Initialize background tasks

    yield  # Application is running

    # Shutdown
    print("Shutting down...")
    # Add any cleanup logic here:
    # - Close database connections
    # - Clear caches
    # - Save state
    # - Close file handles


app = FastAPI(lifespan=lifespan)

# Setting v1 APIs
v1_router = APIRouter(prefix="/v1", tags=["v1"])
v1_router.include_router(auth_router, prefix="/auth", tags=["auth"])
v1_router.include_router(user_router, prefix="/users", tags=["users"])
v1_router.include_router(test_router, prefix="/test", tags=["test"])

app.include_router(v1_router, prefix="/api")

# Add middlewares to the app
__MIDDLEWARES__ = [
    RequestSetupMiddleware,
    ExceptionMiddleware,
    AuthMiddleware,
]

for middleware in reversed(__MIDDLEWARES__):
    app.add_middleware(middleware)
