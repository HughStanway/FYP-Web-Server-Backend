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

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(2))
    def init(self):
        try:
            self.client = weaviate.connect_to_local(
                host="weaviate",
                port=8080,
                grpc_port=50051,
            )

            self._initialized = True
            logging.info("Weaviate client and collection initialised")

        except Exception as e:
            raise DatabaseException(
                f"Error during client and collection setup: {e}", self.client
            )

    def clean_shutdown(self):
        self.client.close()

    def is_init(self) -> bool:
        return self._initialized

    def _error(self, message: str, error: int = 0) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={
                "error": 0,
                "message": message,
            },
        )
    
    def does_collection_exist(self, collection_name: str):
        if any(
                col == collection_name
                for col in self.client.collections.list_all().keys()
            ):
            return True
        return False
    
    def create_collection(self, collection_name: str):
        try:
            self.collection = self.client.collections.create(
                collection_name,
                vectorizer_config=wvc.config.Configure.Vectorizer.none(),
            )

            return JSONResponse(
            status_code=500,
            content={
                "message": "Collection initialised successfully",
            },
        )
        except weaviate.exceptions.WeaviateBaseError as e:
            return self._error(f"Cannot create collection: {e}", 0) # Internal error


    def insert(self, data: dict):
        try:
            super().insert(data)
        except RuntimeError as e:
            logging.error("Database client not initialised")
            return

        try:
            self.collection.data.insert(
                properties={"hash": data["hash"]},
                vector=data["embedding"],
            )
        except weaviate.exceptions.WeaviateBaseError as e:
            logging.error(f"Database client internal error: {e}")
            return

    def query(self, data: dict, collection_name: str):
        try:
            super().query(data)
        except RuntimeError as e:
            return self._error("Database client not initialised")

        try:
            collection = self.client.collections.get(collection_name)

            return collection.query.near_vector(
                near_vector=data["embedding"],
                limit=self.QUERY_LIMIT,
                return_metadata=wvc.query.MetadataQuery(certainty=True),
            )
        except weaviate.exceptions.WeaviateBaseError as e:
            return self._error(f"Database client internal error: {e}")
