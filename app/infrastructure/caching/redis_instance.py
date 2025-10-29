from functools import lru_cache

from redis.asyncio import Redis

from core.dependencies import get_settings

settings = get_settings()


@lru_cache
def get_redis_instance():
    return Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        username=settings.redis_username,
        password=settings.redis_password,
        db=settings.redis_db,
        socket_connect_timeout=5,
    )
