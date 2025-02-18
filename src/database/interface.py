from abc import ABC, abstractmethod


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

    def _check_initialized(self):
        """Helper function to ensure init() was called before using insert/query."""
        if not self._initialized:
            raise RuntimeError("Weaviate has not been initialized. Call init() first.")

    @abstractmethod
    def insert(self, data: dict) -> None:
        """Insert Operation on Database"""
        self._check_initialized()

    @abstractmethod
    def query(self, data: dict) -> dict:
        """Query Operation on Database"""
        self._check_initialized()
