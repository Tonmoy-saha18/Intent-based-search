from functools import wraps
import redis
import pickle
import hashlib
import os
import logging

logger = logging.getLogger(__name__)

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=int(os.getenv("REDIS_DB", 0))
)


def cache(ttl: int = 300, key_builder=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Build cache key
            if key_builder:
                cache_key = key_builder(func, *args, **kwargs)
            else:
                key_parts = [func.__name__] + list(args) + list(kwargs.values())
                cache_key = hashlib.md5(str(key_parts).encode()).hexdigest()

            # Try to get from cache
            try:
                cached = redis_client.get(cache_key)
                if cached:
                    return pickle.loads(cached)
            except Exception as e:
                logger.warning(f"Cache get failed: {str(e)}")

            # Execute function
            result = func(*args, **kwargs)

            # Store in cache
            try:
                redis_client.setex(
                    cache_key,
                    ttl,
                    pickle.dumps(result)
                )
            except Exception as e:
                logger.warning(f"Cache set failed: {str(e)}")

            return result

        return wrapper

    return decorator