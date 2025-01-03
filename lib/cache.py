import redis
import json
from typing import Any, Optional
from lib.helpers import get_environment_setting
from lib.telemetry import OpenTelemetryExporter

OPEN_TELEMETRY_EXPORTER = OpenTelemetryExporter(service_name="QueueWorkerService", local_debug=False)
REDIS_URL = get_environment_setting("REDIS_URL")
DEFAULT_TTL = int(get_environment_setting("CACHE_DEFAULT_TTL") or 24*60*60)
CACHE_PREFIX = "presto_media_cache:"
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
            cached_result = client.get(CACHE_PREFIX+content_hash)
            if cached_result is not None:
                if reset_ttl:
                    client.expire(CACHE_PREFIX+content_hash, ttl)
                response = json.loads(cached_result)
                OPEN_TELEMETRY_EXPORTER.log_execution_status("cache_hit_response", "cache_hit_response")
                return response
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
        if content_hash:
            client = Cache.get_client()
            client.setex(CACHE_PREFIX+content_hash, ttl, json.dumps(result))
            OPEN_TELEMETRY_EXPORTER.log_execution_status("cache_miss_response", "cache_hit_response")
