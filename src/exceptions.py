""""
Core exceptions raised by the Code Search client
"""

import logging

import weaviate

#### ##########
# Error Codes #
###############

# 0: Internal Error
# 1: Missing code snippet from payload
# 2: Malformed field type
# 3: Missing collectionName field
# 4: Cannot create collection that already exists
# 5: Cannot query from collection that doesn't exist


class CodeSearchError(Exception):
    def __init__(self, message: str, error_code: int = 0):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class APIError(CodeSearchError):
    pass


class DatabaseError(CodeSearchError):
    def __init__(
        self, message: str, client: weaviate.Client, error_code: int = 0
    ) -> None:
        super().__init__(message, error_code)
        self.cleanup(client)

    def cleanup(self, client: weaviate.Client) -> None:
        """Ensure client_close is called when the exception is cleaned up."""
        logging.error(
            "Cannot recover from error. Closing Weaviate client connection..."
        )
        if client is not None and client.is_ready():
            client.close()


class RedisClientError(CodeSearchError):
    pass


class EmbeddingError(CodeSearchError):
    pass

class ProcessInsertError(CodeSearchError):
    pass
