import pytest
from unittest.mock import patch, MagicMock
from lib.cache import Cache

# Mock the Redis client and its methods
@pytest.fixture
def mock_redis_client():
    with patch('lib.cache.redis.Redis') as mock_redis:
        yield mock_redis

def test_set_cached_result(mock_redis_client):
    mock_instance = mock_redis_client.from_url.return_value
    content_hash = "test_hash"
    result = {"data": "example"}
    ttl = 3600

    Cache.set_cached_result(content_hash, result, ttl)

    mock_instance.setex.assert_called_once_with(content_hash, ttl, '{"data": "example"}')

def test_get_cached_result_exists(mock_redis_client):
    mock_instance = mock_redis_client.from_url.return_value
    content_hash = "test_hash"
    ttl = 3600
    cached_data = '{"data": "example"}'
    mock_instance.get.return_value = cached_data

    result = Cache.get_cached_result(content_hash, reset_ttl=True, ttl=ttl)

    assert result == {"data": "example"}
    mock_instance.expire.assert_called_once_with(content_hash, ttl)

def test_get_cached_result_not_exists(mock_redis_client):
    mock_instance = mock_redis_client.from_url.return_value
    content_hash = "test_hash"
    mock_instance.get.return_value = None

    result = Cache.get_cached_result(content_hash)

    assert result is None
    mock_instance.expire.assert_not_called()

def test_get_cached_result_no_ttl_reset(mock_redis_client):
    mock_instance = mock_redis_client.from_url.return_value
    content_hash = "test_hash"
    cached_data = '{"data": "example"}'
    mock_instance.get.return_value = cached_data

    result = Cache.get_cached_result(content_hash, reset_ttl=False)

    assert result == {"data": "example"}
    mock_instance.expire.assert_not_called()
