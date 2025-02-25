import hashlib
import logging
import re
from contextlib import asynccontextmanager
from exceptions import APIError, DatabaseError, EmbeddingError, RedisClientError

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from redis_database import RedisDatabase
from voyage_embedding import VoyageEmbedding
from weaviate_database import Weaviate

logging.basicConfig(
    level=logging.INFO, format="%(levelname)s:     [LOGGING]: %(message)s"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    api_instance = app.state.api_instance
    logging.info("Init Application Startup")
    api_instance.startup()
    yield
    logging.info("Init Application Shutdown")
    api_instance.shutdown()


class API:
    def __init__(self):
        self.app = FastAPI(lifespan=lifespan)
        self.app.state.api_instance = self
        self._register_routes()
        self._register_exception_handlers()

        self.database_client: Weaviate = None
        self.embedding_client: VoyageEmbedding = None
        self.redis_client: RedisDatabase = None

    def startup(self):
        logging.info("Startup called")
        self.embedding_client = VoyageEmbedding()
        self.embedding_client.init()

        self.database_client = Weaviate()
        self.database_client.init()

        self.redis_client = RedisDatabase()
        self.redis_client.init()

    def shutdown(self):
        logging.info("Shutdown called")
        self.database_updater.stop_worker()
        self.database_client.clean_shutdown()

    def _compute_hash(self, filetext: str):
        return hashlib.sha256(filetext.encode()).hexdigest()

    def _format_response(self, response):
        res = []
        for result in response:
            snippet = self.redis_client.get(result.properties["hash"])
            res.append({"snippet": snippet, "certainty": result.metadata.certainty})
        return {"response": res}

    def _is_collection_name_valid(self, collection_name: str):
        valid_format = r"^[A-Z][_0-9A-Za-z]*$"
        return bool(re.fullmatch(valid_format, collection_name))

    def _check_field(
        self,
        data: dict,
        field: str,
        missing_error: int,
        type_error: int,
        missing_msg: str,
    ):
        # Check for field in request
        if field not in data:
            raise APIError(missing_msg, missing_error)
        value = data[field]
        # Check field is the correct type
        if not isinstance(value, str):
            raise APIError(
                f"{field} should be type str. Instead got type {type(value)}",
                type_error,
            )
        return value

    def _register_routes(self):
        @self.app.post(
            "/query",
            summary="Query For Similar Code Snippets",
            description="Send a code snippet and get the most similar results from the database based on the embedding.",
        )
        async def query(data: dict):
            """
            This endpoint accepts a JSON payload with two fields: 'payload' and 'collectionName;.
            It computes the embedding of the text using the voyage-code-3 model and
            queries the corresponding database collection using this embedding.
            Returns top k most similar results in the database to the user.
            """

            # Check for code snippet in request and check it is the correct type
            filetext = self._check_field(
                data, "payload", 1, 2, "Missing Request Field: No payload"
            )

            # Check for collection name and check it is the correct type
            collection_name = self._check_field(
                data, "collectionName", 3, 2, "Missing Request Field: No collectionName"
            )

            # Check collection name exists
            if not self.database_client.does_collection_exist(collection_name):
                raise APIError("Cannot query from collection that doesn't exist", 5)

            # Get filetext and embedding
            embedding = self.embedding_client.compute_embedding(filetext)

            # Make database query and process results
            query_result = self.database_client.query(
                {"embedding": embedding}, collection_name
            ).objects
            return self._format_response(query_result)

        @self.app.post(
            "/create",
            summary="Create new collection instance",
            description="Creates a new Vector Embedding Database instance",
        )
        async def create(data: dict):
            """
            This endpoint accepts a JSON payload with a singe field: 'collectionName'.
            It creates a new collection in the database if a collection doesn't already
            exist with that id already.
            """

            # Check for collection name and check it is the correct type
            collection_name = self._check_field(
                data,
                "collectionName",
                3,
                2,
                "Missing Request Field: No collection name",
            )

            # Check collection name is valid format
            if not self._is_collection_name_valid(collection_name):
                raise APIError(
                    "Collection name must follow the format: /^[A-Z][_0-9A-Za-z]*$/", 2
                )

            if self.database_client.does_collection_exist(collection_name):
                raise APIError("Cannot create collection that already exists", 4)

            return self.database_client.create_collection(collection_name)

        @self.app.post(
            "/insert",
            summary="Configure a collection",
            description="Provide the sample data used to populate the embeddings in a database collection",
        )
        async def insert(data: dict):
            """
            Doc string
            """

            # Check for collection name and check it is the correct type
            collection_name = self._check_field(
                data,
                "collectionName",
                3,
                2,
                "Missing Request Field: No collection name",
            )

            # Additional insert logic goes here

    def _register_exception_handlers(self):
        @self.app.exception_handler(HTTPException)
        async def http_exception_handler(request: Request, exc: HTTPException):
            return JSONResponse(
                status_code=exc.status_code,
                content={"message": f"Error: {exc.detail}"},
            )

        async def generic_exception_handler(request: Request, exc):
            error_code = getattr(exc, "error_code", getattr(exc, "error_code", None))
            return JSONResponse(
                status_code=500,
                content={"error": error_code, "message": str(exc.message)},
            )

        # Add generic exception types
        self.app.add_exception_handler(APIError, generic_exception_handler)
        self.app.add_exception_handler(RedisClientError, generic_exception_handler)
        self.app.add_exception_handler(EmbeddingError, generic_exception_handler)
        self.app.add_exception_handler(DatabaseError, generic_exception_handler)


app = API().app
