import logging
import os

import weaviate
import weaviate.classes as wvc
from fastapi.responses import JSONResponse
from tenacity import retry, stop_after_attempt, wait_fixed

from database.database_exception import DatabaseException
from database.interface import DatabaseInterface

logging.basicConfig(
    level=logging.INFO, format="%(levelname)s:     [LOGGING]: %(message)s"
)


class Weaviate(DatabaseInterface):
    """
    Weaviate Class Controls all setup and Interactions
    with the Weeaviate Database
    """

    QUERY_LIMIT = 5

    def __init__(self):
        super().__init__()
        self.client = None
        self.collection = None

        if "COLLECTION_NAME" in os.environ:
            self.collection_name = os.environ["COLLECTION_NAME"]
        else:
            raise KeyError("Environment variable COLLECTION_NAME is missing.")

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(2))
    def init(self) -> None:
        try:
            self.client = weaviate.connect_to_local(
                host="weaviate",
                port=8080,
                grpc_port=50051,
            )

            # Check if the collection exists otherwise create new one
            if any(
                col == self.collection_name
                for col in self.client.collections.list_all().keys()
            ):
                self.collection = self.client.collections.get(self.collection_name)
            else:
                self.collection = self.client.collections.create(
                    self.collection_name,
                    vectorizer_config=wvc.config.Configure.Vectorizer.none(),
                )

            self._initialized = True
            logging.info("Weaviate client and collection initialised")

        except Exception as e:
            raise DatabaseException(
                f"Error during client and collection setup: {e}", self.client
            )

    def clean_shutdown(self) -> None:
        self.client.close()

    def is_init(self) -> bool:
        return self._initialized

    def _error(self, message: str) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={
                "error": 0,
                "message": message,
            },
        )

    def insert(self, data: dict) -> None:
        try:
            super().insert(data)
        except RuntimeError as e:
            logging.error("Database client not initialised")
            return

        if "embedding" not in data:
            logging.error("Embedding missing from insert call")
            return

        if "hash" not in data:
            logging.error("Filetext hash missing from insert call")
            return

        try:
            self.collection.data.insert(
                properties={"hash": data["hash"]},
                vector=data["embedding"],
            )
        except weaviate.exceptions.WeaviateBaseError as e:
            logging.error(f"Database client internal error: {e}")
            return

    def query(self, data: dict) -> dict:
        try:
            super().query(data)
        except RuntimeError as e:
            return self._error("Database client not initialised")

        if "embedding" not in data:
            return self._error("Embedding missing from query call")

        try:
            return self.collection.query.near_vector(
                near_vector=data["embedding"],
                limit=self.QUERY_LIMIT,
                return_metadata=wvc.query.MetadataQuery(certainty=True),
            )
        except weaviate.exceptions.WeaviateBaseError as e:
            return self._error(f"Database client internal error: {e}")
