import logging
import os

import voyageai
from fastapi.responses import JSONResponse
from tenacity import retry, stop_after_attempt, wait_fixed

from embedding.interface import EmbeddingInterface

logging.basicConfig(
    level=logging.INFO, format="%(levelname)s:     [LOGGING]: %(message)s"
)


class VoyageEmbedding(EmbeddingInterface):
    MODEL = "voyage-code-3"

    def __init__(self):
        super().__init__()
        self.voyage_client = None

        if "VOYAGE_API_KEY" not in os.environ:
            raise KeyError("Environment variable VOYAGE_API_KEY is missing.")

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(2))
    def init(self):
        try:
            self.voyage_client = voyageai.Client()
            self._initialized = True
            logging.info("Connection to voyage API successfull")
        except voyageai.error.VoyageError as e:
            raise voyageai.error.APIError(f"Error during embedding setup: {e}")

    def is_init(self) -> bool:
        return self._initialized

    def compute_embedding(self, filetext: str):
        try:
            super().compute_embedding(filetext)
        except RuntimeError as e:
            return JSONResponse(
                status_code=500,
                content={"error": 0, "message": "Embedding client not initialised"},
            )

        try:
            return self.voyage_client.embed([filetext], model=self.MODEL).embeddings[0]
        except voyageai.error.VoyageError as e:
            return JSONResponse(
                status_code=500,
                content={
                    "error": 0,
                    "message": f"Embedding client internal error: {e}",
                },
            )
