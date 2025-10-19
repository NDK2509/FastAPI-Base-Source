from core.app_exceptions import AppException
from pydantic import BaseModel
from fastapi.responses import JSONResponse


class ErrorResponse(BaseModel):
    msg: str
    detail: str | None = None
    status_code: int = 400

    @classmethod
    def from_exception(cls, exc: AppException):
        return cls(msg=exc.msg, detail=exc.detail, status_code=exc.status_code)

    def to_json_response(self):
        return JSONResponse(
            content=self.model_dump(),
            status_code=self.status_code
        )
