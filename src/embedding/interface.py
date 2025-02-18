from abc import ABC, abstractmethod


class EmbeddingInterface(ABC):
    """
    Embedding Interface class ensures there is embedding
    connection to the embedding model
    """

    def __init__(self):
        self._initialized = False

    @abstractmethod
    def init(self) -> None:
        """
        Init Method for Embedding Model Setup
        """

    def _check_initialized(self) -> None:
        """Helper function to ensure init() was called before using insert/query."""
        if not self._initialized:
            raise RuntimeError(
                "Embedding model has not been initialized. Call init() first."
            )

    @abstractmethod
    def compute_embedding(self, filetext: str):
        """Insert Operation on Database"""
        self._check_initialized()
