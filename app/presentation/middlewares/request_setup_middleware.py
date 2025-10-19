import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from core.context import request_id


class RequestSetupMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id.set(str(uuid.uuid4()))
        return await call_next(request)