"""
Interface to connect with Database API
"""

from abc import ABCMeta, abstractmethod


class DatabaseInterface(metaclass=ABCMeta):
    """
    Database Interface class ensures there is a insert
    and query connection to database API
    """

    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, "insert")
            and callable(subclass.insert)
            and hasattr(subclass, "query")
            and callable(subclass.query)
            or NotImplemented
        )

    @abstractmethod
    def init(self) -> None:
        """
        Init Method for Database Setup
        """
        raise NotImplementedError

    @abstractmethod
    def insert(self, data: dict) -> None:
        """Insert Operation on Database"""
        raise NotImplementedError

    @abstractmethod
    def query(self, data: dict) -> dict:
        """Query Operation on Database"""
        raise NotImplementedError
