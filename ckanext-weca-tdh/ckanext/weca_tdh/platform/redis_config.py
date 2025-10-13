import json
import redis
import threading
import time
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
        self.client.hset(f"task:{task_id}", mapping={"status": status, "message": message, "file_path": str(file_path)})
        self.client.expire(f"task:{task_id}", 3600)

    def get_download_status(self, task_id: str):
        return self.client.hgetall(f"task:{task_id}")
    
    def delete_download_task(self, task_id):
        self.client.delete(f"task:{task_id}")
        
    def _token_key(self, user_id: str) -> str:
        return f"databricks:tokens:{user_id}"

    def set_databricks_tokens(self, user_id: str, access_token: str, refresh_token: str, expires_at: int, refresh_expires_at: int):
        token_data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": expires_at,
            "refresh_expires_at": refresh_expires_at
        }
        ttl = refresh_expires_at - int(time.time())
        if ttl <= 0:
            ttl = 1
        
        self.client.set(self._token_key(user_id), json.dumps(token_data), ex=ttl)

    def get_databricks_tokens(self, user_id: str):
        data = self.client.get(self._token_key(user_id))
        if not data:
            return None
        return json.loads(data)

    def delete_databricks_tokens(self, user_id: str):
        self.client.delete(self._token_key(user_id))
        
    def _group_name_key(self, group_id: str) -> str:
        return f"user:group:{group_id}"

    def set_group_name(self, group_id: str, name: str, ttl: int = 86400 * 180):
        """Cache a single AD group name globally"""
        self.client.set(self._group_name_key(group_id), name, ex=ttl)

    def get_group_name(self, group_id: str) -> str | None:
        """Get cached AD group name; return None if missing"""
        return self.client.get(self._group_name_key(group_id))
