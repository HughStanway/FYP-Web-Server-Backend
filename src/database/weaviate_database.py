import logging
import os

import weaviate
import weaviate.classes as wvc
from database_exception import DatabaseException
from interface import DatabaseInterface

logging.basicConfig(
    level=logging.DEBUG, format="%(levelname)s:     [LOGGING]: %(message)s"
)


class Weaviate(DatabaseInterface):
    """
    Weaviate Class Controls all setup and Interactions
    with the Weeaviate Database
    """

    VOYAGE_EMBEDDING_DIMENSION = 1024
    QUERY_LIMIT = 5

    def __init__(self):
        super().__init__()
        self.client = None
        self.collection = None

        if "COLLECTION_NAME" in os.environ:
            self.collection_name = os.environ["COLLECTION_NAME"]
        else:
            raise KeyError("Environment variable COLLECTION_NAME is missing.")

    def init(self) -> None:
        try:
            self.client = weaviate.connect_to_local()

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

    def insert(self, data: dict) -> None:
        super().insert(data)
        if "embedding" not in data:
            raise DatabaseException("Embedding missing from insert call", self.client)

        if "language" not in data:
            raise DatabaseException("Language missing from insert call", self.client)

        if "ts" not in data:
            raise DatabaseException("Timestamp missing from insert call", self.client)

        self.database.collection.data.insert(
            properties={"timestamp": data["ts"], "language": data["language"]},
            vector=data["embedding"],
        )

    def query(self, data: dict) -> dict:
        super().query(data)
        if "embedding" not in data:
            raise DatabaseException("Embedding missing from insert call", self.client)

        return self.database.collection.query.near_vector(
            near_vector=data["embedding"],
            limit=self.QUERY_LIMIT,
            return_metadata=wvc.query.MetadataQuery(certainty=True),
            where={
                "path": ["language"],
                "operator": "Equal",
                "valueString": data["language"],
            },
        )
