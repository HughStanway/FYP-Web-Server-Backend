import hashlib
import re
import logging
from contextlib import asynccontextmanager
from exceptions.api_error import APIError

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

#from database.database_updater import DatabaseUpdater
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

    def startup(self):
        logging.info("Startup called")
        self.embedding_client = VoyageEmbedding()
        self.embedding_client.init()

        self.database_client = Weaviate()
        self.database_client.init()

        #self.database_updater = DatabaseUpdater(self.database_client)
        #self.database_updater.init()
        #self.database_updater.start_worker()

    def shutdown(self):
        logging.info("Shutdown called")
        self.database_updater.stop_worker()
        self.database_client.clean_shutdown()

    def _compute_hash(self, filetext: str):
        return hashlib.sha256(filetext.encode()).hexdigest()
    
    def _format_response(self, response):
        res = []
        '''
        for result in response:
            snippet = self.database_updater.get_from_redis(result.properties["hash"])
            res.append(
                {
                    "snippet": snippet,
                    "certainty": result.metadata.certainty
                }
            )
        '''
        return {"response": res}
        
    def _is_collection_name_valid(self, collection_name: str):
        valid_format = r"^[A-Z][_0-9A-Za-z]*$"
        return bool(re.fullmatch(valid_format, collection_name))

    def _register_routes(self):
        @self.app.post(
            "/query",
            summary="Query For Similar Code Snippets",
            description="Send a code snippet and get the most similar results from the database based on the embedding.",
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
            
            # Check for collection name
            if "collectionName" not in data:
                raise APIError("Missing Request Field: No collectionName", 3)
            
            # Check collection name is the correct type
            if not isinstance(data["collectionName"], str):
                raise APIError(
                    f"collectionName should be type str. Instead got type {type(data['collectionName'])}",
                    2,
                )
            
            # Check collection name exists
            collection_name = data['collectionName']
            if not self.database_client.does_collection_exist(collection_name):
                raise APIError("Cannot query from collection that doesn't exist", 5)

            # Check embedding client is initialised
            if (
                not isinstance(self.embedding_client, VoyageEmbedding)
                or not self.embedding_client.is_init()
            ):
                raise APIError("Internal Error: Embedding Client not initialized", 0)

            # Get filetext and embedding
            filetext = data["payload"]
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
            
            # Make database query and process results
            query_result = self.database_client.query({"embedding": embedding}, collection_name).objects
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

            # Check for collection name
            if "collectionName" not in data:
                raise APIError("Missing Request Field: No collection name", 3)
            collection_name = data['collectionName']
            
            # Check collection name is the correct type
            if not isinstance(collection_name, str):
                raise APIError(
                    f"collectionName should be type str. Instead got type {type(data['collectionName'])}",
                    2,
                )
            
            # Check collection name is valid format
            if not self._is_collection_name_valid(collection_name):
                raise APIError("Collection name must follow the format: /^[A-Z][_0-9A-Za-z]*$/", 2)

            if self.database_client.does_collection_exist(collection_name):
                raise APIError("Cannot create collection that already exists", 4)
            
            return self.database_client.create_collection(collection_name)

        @self.app.post(
            "/insert",
            summary="Configure a collection",
            description="Provide the sample data used to populate the embeddings in a database collection",
        )
        async def insert(data: dict):
            # Check for collection name
            if "collectionName" not in data:
                raise APIError("Missing Request Field: No collection name", 3)

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
