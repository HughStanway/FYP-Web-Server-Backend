import logging
from exceptions import DatabaseError

import weaviate
import weaviate.classes as wvc
from fastapi.responses import JSONResponse
from tenacity import retry, stop_after_attempt, wait_fixed

from interface import DatabaseInterface

logging.basicConfig(
    level=logging.INFO, format="%(levelname)s:     [LOGGING]: %(message)s"
)


class Weaviate(DatabaseInterface):
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

        except weaviate.exceptions.WeaviateBaseError as e:
            raise DatabaseError(
                f"Error during client and collection setup: {e}", self.client
            )

    def clean_shutdown(self):
        self.client.close()

    def is_init(self):
        return self._initialized

    def _error(self, message: str, error: int = 0):
        raise DatabaseError(message, error)

    def does_collection_exist(self, collection_name: str):
        try:
            if any(
                col == collection_name
                for col in self.client.collections.list_all().keys()
            ):
                return True
            return False
        except weaviate.exceptions.WeaviateBaseError as e:
            self._error(f"Cannot create collection: {e}", 0)

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
            self._error(f"Cannot create collection: {e}", 0)

    def insert(self, data: dict):
        super().insert(data)

        try:
            self.collection.data.insert(
                properties={"hash": data["hash"]},
                vector=data["embedding"],
            )
        except weaviate.exceptions.WeaviateBaseError as e:
            self._error(f"Database client internal error: {e}", 0)

    def query(self, data: dict, collection_name: str):
        super().query(data)

        try:
            collection = self.client.collections.get(collection_name)

            return collection.query.near_vector(
                near_vector=data["embedding"],
                limit=self.QUERY_LIMIT,
                return_metadata=wvc.query.MetadataQuery(certainty=True),
            )
        except weaviate.exceptions.WeaviateBaseError as e:
            self._error(f"Database client internal error: {e}", 0)
