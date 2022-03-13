import logging
import functools

from abc import ABC, abstractmethod

from datetime import datetime
from typing import Any

import uuid

class ApplicationException(Exception):
    """Base class for all application exception"""
    pass

class ValidationException(ApplicationException):
    """Something happened about the required input values"""
    def __init__(self, attribute_name: str, error_message: Any) -> None:
        self.attribute_name = attribute_name
        self.error_message = error_message

class RepositoryException(ApplicationException):
    """Exception throws because of the errors in the repository layer"""
    pass

class ResourceNotFoundException(RepositoryException):
    """No Resource was found for a given type and id"""
    def __init__(self, resource_type: str, resource_id: Any) -> None:
        self.resource_type = resource_type
        self.resource_id = resource_id

class User:
    """A user within the system"""
    def __init__(self, user_id: str) -> None:
        self.user_id = user_id

class AuthorMetadata:
    """Author metadata"""
    def __self__(self, author_id: str, date: datetime) -> None:
        self.author_id = author_id
        self.date = date

class DataPage:
    """Metadata for performing paginated queries"""
    def __init__(self, page_size: int = 100, continuation_token: str = None) -> None:
        self.page_size = page_size
        self.continuation_token = continuation_token

class DomainEntity:
    id: str
    
    """A uniquely identified domain entity"""
    def __init__(self, id: str = None) -> None:
        self.id = id or str(uuid.uuid4())

    def __eq__(self, other: Any) -> bool:
        if type(self) != type(other):
            return False

        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

def wrap_exceptions(function):
    """
    Generic exception handler that catches any exceptions and retrows them as ApplicationException instances
    """
    @functools.wraps(function)
    def wrap(*args, **kwargs):
        logging.debug(f"Before {function.__name__}()")
        try:
            return function(*args, **kwargs)
        except Exception as e:
            logging.error(f"Whops, when running {function.__name__}():\n{e}")
            raise ApplicationException(e)
        finally:
            logging.debug(f"After {function.__name__}()")

    return wrap

class ObjectStore:
    """
    Generic abstraction of an object store.
    """
    @abstractmethod
    def store(self, object_key: str, content: str) -> None:
        pass

    @abstractmethod
    def load(self, object_key: str) -> str:
        pass

    @abstractmethod
    def delete(self, object_key: str) -> None:
        pass

class ContentUploadException(ApplicationException):
    """
    Exception thrown by ObjectStore instances if issues are found when saving content
    """
    pass
