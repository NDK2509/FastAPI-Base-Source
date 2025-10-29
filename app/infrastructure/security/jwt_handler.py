from datetime import timedelta, datetime
from typing import Any

import jwt
import pytz
from jwt import ExpiredSignatureError, InvalidTokenError

from core.app_exceptions import AuthException, AccessTokenExpiredException, RefreshTokenExpiredException
from core.dependencies import get_settings

settings = get_settings()

class JwtHandler:
    @staticmethod
    def __generate_token(payload: dict, secret: str) -> str:
        return jwt.encode(payload, secret, settings.jwt_algorithm)

    @classmethod
    def generate_access_token(cls, payload: dict) -> str:
        expiration = datetime.now(tz=pytz.timezone(settings.tz)) + timedelta(seconds=settings.jwt_access_expiration)
        payload.update({"exp": expiration})
        return cls.__generate_token(payload, settings.jwt_access_secret)

    @classmethod
    def generate_refresh_token(cls, payload: dict) -> str:
        expiration = datetime.now(tz=pytz.timezone(settings.tz)) + timedelta(seconds=settings.jwt_refresh_expiration)
        payload.update({"exp": expiration})
        return cls.__generate_token(payload, settings.jwt_refresh_secret)

    @staticmethod
    def __verify_token(token: str, secret: str) -> Any:
        return jwt.decode(token, secret, algorithms=[settings.jwt_algorithm])

    @classmethod
    def verify_access_token(cls, token: str) -> Any:
        try:
            return cls.__verify_token(token, settings.jwt_access_secret)
        except ExpiredSignatureError:
            raise AccessTokenExpiredException()
        except InvalidTokenError:
            raise AuthException()

    @classmethod
    def verify_refresh_token(cls, token: str) -> Any:
        try:
            return cls.__verify_token(token, settings.refresh_token_secret)
        except ExpiredSignatureError:
            raise RefreshTokenExpiredException()
        except InvalidTokenError:
            raise AuthException()
