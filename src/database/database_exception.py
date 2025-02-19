import logging

import weaviate

logging.basicConfig(
    level=logging.INFO, format="%(levelname)s:     [LOGGING]: %(message)s"
)


class DatabaseException(Exception):
    def __init__(self, message: str, client: weaviate.Client) -> None:
        super().__init__(message)
        self.cleanup(client)

    def cleanup(self, client: weaviate.Client) -> None:
        """Ensure client_close is called when the exception is cleaned up."""
        logging.error(
            "Cannot recover from error. Closing Weaviate client connection..."
        )
        if client is not None and client.is_ready():
            client.close()
