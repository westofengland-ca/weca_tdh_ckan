import logging
from urllib.parse import urlparse

import redis

log = logging.getLogger(__name__)


def get_redis_client(redis_url: str):
    """Parses Redis URL and returns a Redis client instance."""
    parsed_url = urlparse(redis_url)

    host = parsed_url.hostname
    port = parsed_url.port
    db = int(parsed_url.path.lstrip("/")) if parsed_url.path else 0
    password = parsed_url.password
    use_ssl = parsed_url.scheme == "rediss"  # Enable SSL if scheme is 'rediss'

    return redis.StrictRedis(
        host=host,
        port=port,
        db=db,
        password=password,
        decode_responses=True,
        ssl=use_ssl
    )
