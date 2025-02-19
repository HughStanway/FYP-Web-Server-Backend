import logging
from contextlib import asynccontextmanager
from exceptions.api_error import APIError

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

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

    def startup(self) -> None:
        logging.info("Startup called")
        self.embedding_client = VoyageEmbedding()
        self.embedding_client.init()

        self.database_client = Weaviate()
        self.database_client.init()

    def shutdown(self) -> None:
        logging.info("Shutdown called")

    def _register_routes(self):
        @self.app.post("/query")
        async def query(data: dict):
            # Check for code snippet in request
            if "payload" not in data:
                raise APIError("Missing Request Field: No payload", 1)

            # Check payload is the correct type
            if not isinstance(data["payload"], str):
                raise APIError(
                    f"Payload should be type str. Instead got type {type(data['payload'])}",
                    2,
                )

            if (
                not isinstance(self.embedding_client, VoyageEmbedding)
                or not self.embedding_client.is_init()
            ):
                raise APIError("Internal Error: Embedding Client not initialized", 0)

            filetext = data["payload"]
            embedding = self.embedding_client.compute_embedding(filetext)

            if isinstance(embedding, JSONResponse):
                return embedding

            return {"embedding": embedding}

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
