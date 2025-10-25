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


class InvalidCredentialsException(AuthException):
    msg = "Invalid credentials!"
    detail = (
        "Please check your username and password"
    )

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


class UserAlreadyExistsException(AppException):
    status_code = HTTPStatus.CONFLICT
    msg = "User already exists!"


class UsernameAlreadyExistsException(AppException):
    status_code = HTTPStatus.CONFLICT
    msg = "Username already exists!"


class EmailAlreadyExistsException(AppException):
    status_code = HTTPStatus.CONFLICT
    msg = "Email already exists!"
