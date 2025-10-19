from functools import lru_cache
from fastapi import Request

from core.environment_setting import Settings


@lru_cache
def get_settings():
    return Settings()

def get_authenticated_user(request: Request):
    return request.state.user
