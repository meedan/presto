import redis
import json
from typing import Any, Optional
from lib.helpers import get_environment_setting

REDIS_URL = get_environment_setting("REDIS_URL")
DEFAULT_TTL = int(get_environment_setting("CACHE_DEFAULT_TTL") or 24*60*60)
class Cache:
    @staticmethod
    def get_client() -> redis.Redis:
        """
        Get a Redis client instance using the provided REDIS_URL.

        Returns:
            redis.Redis: Redis client instance.
        """
        return redis.Redis.from_url(REDIS_URL)

    @staticmethod
    def get_cached_result(content_hash: str, reset_ttl: bool = True, ttl: int = DEFAULT_TTL) -> Optional[Any]:
        """
        Retrieve the cached result for the given content hash. By default, reset the TTL to 24 hours.

        Args:
            content_hash (str): The key for the cached content.
            reset_ttl (bool): Whether to reset the TTL upon access. Default is True.
            ttl (int): Time-to-live for the cache in seconds. Default is 86400 seconds (24 hours).

        Returns:
            Optional[Any]: The cached result, or None if the key does not exist.
        """
        if content_hash:
            client = Cache.get_client()
            cached_result = client.get(content_hash)
            if cached_result is not None:
                if reset_ttl:
                    client.expire(content_hash, ttl)
                return json.loads(cached_result)
        return None

    @staticmethod
    def set_cached_result(content_hash: str, result: Any, ttl: int = DEFAULT_TTL) -> None:
        """
        Store the result in the cache with the given content hash and TTL.

        Args:
            content_hash (str): The key for the cached content.
            result (Any): The result to cache.
            ttl (int): Time-to-live for the cache in seconds. Default is 86400 seconds (24 hours).
        """
        client = Cache.get_client()
        client.setex(content_hash, ttl, json.dumps(result))
