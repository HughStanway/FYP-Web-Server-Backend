import logging
import queue
import threading

import redis
from tenacity import retry, stop_after_attempt, wait_fixed

logging.basicConfig(
    level=logging.INFO, format="%(levelname)s:     [LOGGING]: %(message)s"
)


class DatabaseUpdater:
    def __init__(self, database_client) -> None:
        self._initialized = False
        self.running = True
        self.redis_client = None
        self.database_client = database_client
        self.task_queue = queue.Queue()

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(2))
    def init(self) -> None:
        try:
            self.redis_client = redis.Redis(
                host="redis", port=6379, decode_responses=True
            )
            self.redis_client.ping()  # Check for successfull connection
            self._initialized = True
            logging.info("Database updater initialised")
        except redis.exceptions.RedisError as e:
            raise RuntimeError("fError connecting to redis: {e}")

    def _process_queue(self) -> None:
        """Background worker that processes the in-memory queue"""
        while self.running:
            try:
                filetext, filetext_hash, embedding = self.task_queue.get(timeout=1)
                logging.info("Insert into redis called")

                # If filetext_hash is not in redis store it,
                # otherwise ingore and continue
                if not self.redis_client.exists(filetext_hash):
                    self.redis_client.set(filetext_hash, filetext)
                    self.database_client.insert(
                        {"hash": filetext_hash, "embedding": embedding}
                    )
                    logging.info("New database entry inserted")
            except queue.Empty:
                continue
            except Exception:
                logging.error("Error inserting new query. Skipping")

    def is_init(self) -> bool:
        return self._initialized

    def start_worker(self) -> None:
        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.worker_thread.start()
        logging.info("Database updater worker thread started")

    def stop_worker(self) -> None:
        self.running = False
        self.worker_thread.join()

    def add_to_queue(self, *items) -> None:
        self.task_queue.put(items)
