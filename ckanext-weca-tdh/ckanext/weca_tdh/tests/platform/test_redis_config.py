from unittest.mock import MagicMock, patch

import pytest
from redis import StrictRedis

from ckanext.weca_tdh.platform.redis_config import RedisConfig


@pytest.fixture
def mock_redis():
    with patch('redis.StrictRedis') as mock_redis_class:
        yield mock_redis_class

@pytest.fixture
def redis_config(mock_redis):
    return RedisConfig('redis://localhost:6379/0')


def test_singleton_instance(redis_config):
    """Test if RedisConfig uses singleton pattern"""
    instance_1 = redis_config
    instance_2 = RedisConfig('redis://localhost:6379/0')
    
    assert instance_1 is instance_2, "RedisConfig should return the same instance"


def test_redis_initialisation(redis_config, mock_redis):
    mock_redis.return_value = MagicMock(spec=StrictRedis)
    
    # Access the Redis client through the config
    redis_config._initialise('redis://localhost:6379/1')

    # Check if StrictRedis was initialized correctly with parsed URL params
    mock_redis.assert_called_with(
        host='localhost',
        port=6379,
        db=1,
        password=None,
        decode_responses=True,
        ssl=False
    )


def test_set_download_status(redis_config, mock_redis):
    mock_redis.return_value = MagicMock(spec=StrictRedis)
    redis_config.client = mock_redis.return_value
    
    task_id = "12345"
    status = "in_progress"
    message = "Downloading file"
    file_path = "/path/to/file"
    
    redis_config.set_download_status(task_id, status, message, file_path)
    
    # Check if the hset method was called on the Redis client
    redis_config.client.hset.assert_called_once_with(
        f"task:{task_id}",
        mapping={"status": status, "message": message, "file_path": str(file_path)}
    )


def test_get_download_status(redis_config, mock_redis):
    mock_redis.return_value = MagicMock(spec=StrictRedis)
    redis_config.client = mock_redis.return_value
    
    task_id = "12345"
    expected_response = {
        "status": "completed",
        "message": "Download finished",
        "file_path": "/path/to/file"
    }
    
    redis_config.client.hgetall.return_value = expected_response
    result = redis_config.get_download_status(task_id)
    
    redis_config.client.hgetall.assert_called_once_with(f"task:{task_id}")
    assert result == expected_response, f"Expected {expected_response}, but got {result}"


def test_delete_download_task(redis_config, mock_redis):
    mock_redis.return_value = MagicMock(spec=StrictRedis)
    redis_config.client = mock_redis.return_value
    task_id = "12345"
    
    redis_config.delete_download_task(task_id)
    redis_config.client.delete.assert_called_once_with(f"task:{task_id}")
