from starlette.middleware.base import BaseHTTPMiddleware

from core.app_exceptions import AppException, SystemException
from core.error_response import ErrorResponse
from core.logging_config import get_logger


logger = get_logger("exception_middleware")

class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            return await call_next(request)
        except AppException as e:
            logger.error(e.msg)
            return ErrorResponse.from_exception(e).to_json_response()
        except Exception as e:
            logger.error(e)
            return ErrorResponse.from_exception(SystemException()).to_json_response()
