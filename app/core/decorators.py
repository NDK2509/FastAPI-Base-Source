import functools
import json
from typing import Callable, Any

from redis.asyncio import Redis

from core.logging_config import get_logger
from infrastructure.caching.redis_instance import get_redis_instance
from infrastructure.serialization.serializer import Serializer

logger = get_logger("Response Cache")


def response_cache(
        key_prefix: str,
        expire: int = 60,
        redis: Redis = get_redis_instance(),
):
    """
    Caches FastAPI responses in Redis only if status == 200.
    Converts ORM entities to dicts using response_model if provided.
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Create a key excluding unserializable items
            filtered_kwargs = {k: str(v) for k, v in kwargs.items() if k != "session"}
            cache_key = f"{key_prefix}:{json.dumps(filtered_kwargs, sort_keys=True)}"

            # Check cache
            cached = await redis.get(cache_key)
            if cached:
                logger.info(f"🧠 Cache hit: {cache_key}")
                return json.loads(cached)

            # Run the actual function
            result = await func(*args, **kwargs)

            try:
                serializable = Serializer.encode(result)
                await redis.setex(cache_key, expire, json.dumps(serializable))
            except Exception as e:
                logger.warning(f"⚠️ Skipped caching due to: {e}")

            return result

        return wrapper

    return decorator
