from datetime import timedelta, datetime

import pytz
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from core.dependencies import get_settings
from core.app_exceptions import AuthException, AccessTokenExpiredException, RefreshTokenExpiredException

settings = get_settings()

class JwtHandler:
    @classmethod
    def __generate_token(cls, payload: dict, secret: str) -> str:
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

    @classmethod
    def __verify_token(cls, token: str, secret: str) -> any:
        return jwt.decode(token, secret, algorithms=[settings.jwt_algorithm])

    @classmethod
    def verify_access_token(cls, token: str) -> any:
        try:
            return cls.__verify_token(token, settings.jwt_access_secret)
        except ExpiredSignatureError:
            raise AccessTokenExpiredException()
        except InvalidTokenError:
            raise AuthException()

    @classmethod
    def verify_refresh_token(cls, token: str) -> any:
        try:
            return cls.__verify_token(token, settings.refresh_token_secret)
        except ExpiredSignatureError:
            raise RefreshTokenExpiredException()
        except InvalidTokenError:
            raise AuthException()
