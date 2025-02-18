import weaviate


class DatabaseException(Exception):
    def __init__(self, message: str, client: weaviate.Client) -> None:
        super().__init__(message)
        self.cleanup(client)

    def cleanup(self, client: weaviate.Client) -> None:
        """Ensure client_close is called when the exception is cleaned up."""
        print("Cannot recover from error. Closing Weaviate client connection...")
        if client is not None and client.is_ready():
            client.close()
