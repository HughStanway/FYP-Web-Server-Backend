import logging

import redis
from fastapi.responses import JSONResponse
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
            raise RuntimeError(f"Error connecting to redis: {e}")

    def _error(self, message: str, error: int = 0) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={
                "error": error,
                "message": message,
            },
        )

    def get(self, key: str):
        if not self._initialized:
            return self._error("Redis client not initialised. Call init() first.")

        try:
            if self._redis_client.exists(key):
                return self._redis_client.get(key)
        except redis.exceptions.RedisError as e:
            return self._error(f"Redis database error: {e}")

    def put(self, key: str, value: str):
        if not self._initialized:
            return self._error("Redis client not initialised. Call init() first.")

        try:
            self._redis_client.set(key, value)
        except redis.exceptions.RedisError as e:
            return self._error(f"Redis database error: {e}")
