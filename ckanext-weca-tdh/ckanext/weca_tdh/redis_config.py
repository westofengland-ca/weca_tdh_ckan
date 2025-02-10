import redis
import threading
from urllib.parse import urlparse


class RedisConfig:
    """Manage Redis configuration"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, redis_url: str):
        """Ensure only one Redis connection is created"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialise(redis_url)
        return cls._instance

    def _initialise(self, redis_url: str):
        """Creates Redis client instance."""
        parsed_url = urlparse(redis_url)

        host = parsed_url.hostname
        port = parsed_url.port
        db = int(parsed_url.path.lstrip("/")) if parsed_url.path else 0
        password = parsed_url.password
        use_ssl = parsed_url.scheme == "rediss" # Enable SSL if scheme is 'rediss'

        self.client = redis.StrictRedis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True,
            ssl=use_ssl
        )

    def set_download_status(self, task_id: str, status: str, message: str, file_path=None):
        self.client.hset(f"task:{task_id}", mapping={"status": str(status), "message": str(message), "file_path": str(file_path)})

    def get_download_status(self, task_id: str):
        return self.client.hgetall(f"task:{task_id}")
    
    def delete_download_task(self, task_id):
        self.client.delete(f"task:{task_id}")
