from functools import lru_cache

from core.environment_setting import Settings


@lru_cache
def get_settings():
    return Settings()
