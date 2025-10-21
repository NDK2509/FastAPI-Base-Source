from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from core.dependencies import get_settings
from domain.repositories.user_repository import UserRepository
from core.app_exceptions import AuthTokenMissingException, UserIdMissingInTokenException, AuthException
from infrastructure.database.config import get_session
from infrastructure.security.jwt_handler import JwtHandler

settings = get_settings()


class AuthMiddleware(BaseHTTPMiddleware):
    __DISABLE_AUTH_PATHS__ = [
        "/docs", "/openapi.json", "/redoc",
        "/api/v1/auth/login",
        "/api/v1/auth/google"
    ]

    async def dispatch(self, request: Request, call_next):
        print(request.url.path)
        print(request.url.path.startswith("/api/v1/auth/google"))
        if not any(request.url.path.startswith(p)
                   for p in self.__DISABLE_AUTH_PATHS__):
            token = request.cookies.get('access_token', None)
            if not token:
                raise AuthTokenMissingException()

            decoded_token = JwtHandler.verify_access_token(token)
            user_id = decoded_token.get("id", None)
            if not user_id:
                raise UserIdMissingInTokenException()

            with next(get_session()) as session:
                # Get user from db
                user = UserRepository(session).get_by_id(user_id)
                # Check whether user is existing
                if not user:
                    raise AuthException()

                # Save authenticated user to request state
                request.state.user = user

        return await call_next(request)