import logging
from exceptions import RedisClientError

import redis
import redis.exceptions

logging.basicConfig(
    level=logging.INFO, format="%(levelname)s:     [LOGGING]: %(message)s"
)


class RedisDatabase:
    def __init__(self):
        self._initialized = False
        self._redis_client = None

    def init(self):
        try:
            self._redis_client = redis.Redis(
                host="redis", port=6379, decode_responses=True
            )
            self._redis_client.ping()  # Check for successfull connection
            self._initialized = True
            logging.info("Redis client initialised")
        except redis.exceptions.RedisError as e:
            raise RedisClientError(f"Error connecting to redis: {e}", 0)

    def _check_init(self):
        if not self._initialized:
            raise RedisClientError(
                "Redis client not initialised. Call init() first.", 0
            )

    def get(self, key: str):
        self._check_init()

        try:
            if self._redis_client.exists(key):
                return self._redis_client.get(key)
        except redis.exceptions.RedisError as e:
            raise RedisClientError(f"Redis database error: {e}", 0)

    def put(self, key: str, value: str):
        self._check_init

        try:
            self._redis_client.set(key, value)
        except redis.exceptions.RedisError as e:
            raise RedisClientError(f"Redis database error: {e}", 0)
