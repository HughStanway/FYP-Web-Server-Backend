import logging
from contextlib import asynccontextmanager
from exceptions.api_error import APIError

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    api_instance = app.state.api_instance
    logging.info("[-] Init Application Startup")
    api_instance.startup()
    yield
    logging.info("[-] Init Application Shutdown")
    api_instance.shutdown()

class API:
    def __init__(self):
        self.app = FastAPI(lifespan=lifespan)
        self.app.state.api_instance = self
        self._register_routes()
        self._register_exception_handlers()
    
    def startup(self) -> None:
        logging.info("Startup called")

    def shutdown(self) -> None:
        logging.info("Shutdown called")

    def _register_routes(self):
        @self.app.post("/query")
        async def query():
            return {"response": "Test Message"}

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
                content={"error": f"Internal Server Error: {str(exc)}"},
            )

app = API().app
