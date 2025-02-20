import hashlib
import logging
from contextlib import asynccontextmanager
from exceptions.api_error import APIError

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from database.database_updater import DatabaseUpdater
from database.weaviate_database import Weaviate
from embedding.voyage_embedding import VoyageEmbedding

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

        self.database_client = None
        self.embedding_client = None
        self.database_updater = None

    def startup(self) -> None:
        logging.info("Startup called")
        self.embedding_client = VoyageEmbedding()
        self.embedding_client.init()

        self.database_client = Weaviate()
        self.database_client.init()

        self.database_updater = DatabaseUpdater(self.database_client)
        self.database_updater.init()
        self.database_updater.start_worker()

    def shutdown(self) -> None:
        logging.info("Shutdown called")
        self.database_updater.stop_worker()
        self.database_client.clean_shutdown()

    def _compute_hash(self, filetext: str) -> str:
        return hashlib.sha256(filetext.encode()).hexdigest()

    def _register_routes(self):
        @self.app.post(
            "/query",
            summary="Query For Similar Snippets",
            description="Send a payload and get the result from the database based on the embedding.",
        )
        async def query(data: dict):
            """
            This endpoint accepts a JSON payload with a singe field: 'payload'.
            It computes the embedding of the text using the voyage-code-3 model and
            queries the database using this embedding.
            Returns top k most similar results in the database to the user.
            """

            # Check for code snippet in request
            if "payload" not in data:
                raise APIError("Missing Request Field: No payload", 1)

            # Check payload is the correct type
            if not isinstance(data["payload"], str):
                raise APIError(
                    f"Payload should be type str. Instead got type {type(data['payload'])}",
                    2,
                )

            # Check embedding client is initialised
            if (
                not isinstance(self.embedding_client, VoyageEmbedding)
                or not self.embedding_client.is_init()
            ):
                raise APIError("Internal Error: Embedding Client not initialized", 0)

            # Get filetext, it's hash and embedding
            filetext = data["payload"]
            filetext_hash = self._compute_hash(filetext)
            embedding = self.embedding_client.compute_embedding(filetext)

            # Check if embedding client returned an error
            if isinstance(embedding, JSONResponse):
                return embedding

            # Check database client is initialised
            if (
                not isinstance(self.database_client, Weaviate)
                or not self.database_client.is_init()
            ):
                raise APIError("Internal Error: Database Client not initialized", 0)

            # Insert query into database if client is initialized,
            # on a seperate thread for efficiency
            if (
                isinstance(self.database_updater, DatabaseUpdater)
                and self.database_updater.is_init()
            ):
                self.database_updater.add_to_queue(filetext, filetext_hash, embedding)

            # Make database query process results
            query_result = self.database_client.query({"embedding": embedding})

            return query_result

    def _register_exception_handlers(self):
        @self.app.exception_handler(HTTPException)
        async def http_exception_handler(request: Request, exc: HTTPException):
            return JSONResponse(
                status_code=exc.status_code,
                content={"message": f"Error: {exc.detail}"},
            )

        @self.app.exception_handler(APIError)
        async def general_exception_handler(request: Request, exc: APIError):
            return JSONResponse(
                status_code=500,
                content={"error": exc.error_code, "message": str(exc.message)},
            )


app = API().app
