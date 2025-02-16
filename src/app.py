# pylint: skip-file

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

class API:
    def __init__(self):
        self.app = FastAPI()
        self._register_routes()
        self._register_exception_handlers()
        self._register_startup_event()

    def _register_routes(self):
        @self.app.post("/query")
        async def query():
            raise ValueError("Some error")

    def _register_exception_handlers(self):
        @self.app.exception_handler(HTTPException)
        async def http_exception_handler(request: Request, exc: HTTPException):
            return JSONResponse(
                status_code=exc.status_code,
                content={"message": f"Error: {exc.detail}"},
            )

        @self.app.exception_handler(Exception)
        async def general_exception_handler(request: Request, exc: Exception):
            return JSONResponse(
                status_code=500,
                content={"error": f"Internal Server Error: {str(exc)}"},
            )

    def _register_startup_event(self):
        @self.app.on_event("startup")
        async def on_startup():
            # Setup database instance here
            print("Application is starting up")

app = API().app