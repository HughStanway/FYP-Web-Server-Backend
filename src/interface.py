"""
Defines interfaces used by the system
"""

from abc import ABC, abstractmethod
from exceptions import DatabaseError, EmbeddingError


class DatabaseInterface(ABC):
    """
    Database Interface class ensures there is a insert
    and query connection to database API
    """

    def __init__(self):
        self._initialized = False

    @abstractmethod
    def init(self) -> None:
        """
        Init Method for Database Setup
        """

    def _check_initialized(self) -> None:
        """Helper function to ensure init() was called before using insert/query."""
        if not self._initialized:
            raise DatabaseError(
                "Database has not been initialized. Call init() first.", 0
            )

    @abstractmethod
    def insert(self, data: dict) -> None:
        """Insert Operation on Database"""
        self._check_initialized()

    @abstractmethod
    def query(self, data: dict) -> dict:
        """Query Operation on Database"""
        self._check_initialized()


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
            raise EmbeddingError(
                "Embedding model has not been initialized. Call init() first.", 0
            )

    @abstractmethod
    def compute_embedding(self, filetext: str):
        """Insert Operation on Database"""
        self._check_initialized()
