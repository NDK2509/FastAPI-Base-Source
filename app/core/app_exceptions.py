from http import HTTPStatus


class AppException(Exception):
    status_code: int
    msg: str
    detail: str | None = None


class SystemException(AppException):
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    msg = "Internal server error!"


class AuthException(AppException):
    status_code = HTTPStatus.UNAUTHORIZED
    msg = "Authentication failed!"


class AccessTokenExpiredException(AuthException):
    msg = "Access token expired!"
    detail = (
        "Please login again to get a new access token"
    )


class RefreshTokenExpiredException(AuthException):
    msg = "Refresh token expired!"
    detail = (
        "Please login again to get a new refresh token"
    )


class AuthTokenMissingException(AuthException):
    msg = "Authentication token missing!"


class UserIdMissingInTokenException(AuthException):
    msg = "User id missing in token!"
    detail = (
        "Please login again to get a new access token"
    )