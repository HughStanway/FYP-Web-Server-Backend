import logging
import os

import voyageai
from interface import EmbeddingInterface

logging.basicConfig(
    level=logging.DEBUG, format="%(levelname)s:     [LOGGING]: %(message)s"
)


class VoyageEmbedding(EmbeddingInterface):
    MODEL = "voyage-code-3"

    def __init__(self):
        super().__init__()
        self.voyage_client = None

        if "VOYAGE_API_KEY" not in os.environ:
            raise KeyError("Environment variable VOYAGE_API_KEY is missing.")

    def init(self):
        try:
            self.voyage_client = voyageai.Client()
            self._initialized = True
            logging.info("Connection to voyage API successfull")
        except voyageai.error.VoyageError as e:
            raise voyageai.error.APIError(f"Error during embedding setup: {e}")

    def compute_embedding(self, filetext: str):
        super().compute_embedding(filetext)
        try:
            return self.voyage_client.embed([filetext], model=self.MODEL).embeddings[0]
        except voyageai.error.VoyageError as e:
            logging.error(f"Voyage API Error: {e}")
            return None
