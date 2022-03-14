import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List

from mynotes.core.architecture import (DomainEntity, ObjectStore, ResourceNotFoundException, User,
                                       wrap_exceptions)
from mynotes.core.utils.common import now


class NoteType(Enum):
    """Supported note types (free notes and interview notes)"""
    FREE = "F"
    INTERVIEW = "I"

@dataclass
class Note(DomainEntity):
    author_id: str
    type: NoteType
    creation_time: datetime
    tags: List[str]
    version: int

    """Entity class representing metadata associated to a Note entity"""
    def __init__(self, id: str = None, author_id: str = None, type: NoteType = None, creation_time: datetime = None, tags: List[str] = None, version: int = None) -> None:
        super().__init__(id)
        self.author_id = author_id
        self.creation_time = creation_time
        self.type = type or NoteType.FREE
        self.tags = tags
        self.version = version or None

class NoteRepository(ABC):
    @abstractmethod
    def save(self, note: Note) -> None:
        pass

    @abstractmethod
    def find_by_id(self, id: str) -> None:
        pass

    @abstractmethod
    def delete_by_id(self, id: str) -> None:
        pass

    @abstractmethod
    def find_all(self) -> None:
        pass

@wrap_exceptions
class NoteUseCases:
    """
        Use cases supported for Notes.
    """
    bucket_adapter: ObjectStore
    note_repository: NoteRepository

    def __init__(self, bucket_adapter: ObjectStore, note_repository: NoteRepository) -> None:
        self.bucket_adapter = bucket_adapter
        self.note_repository = note_repository

    def create_note(self, author: User, content: str, tags: List[str] = None) -> Note:
        """
        Create a new note, based on Markdown standard.
    
        Args:
            author: the identified for the user who is creating this note
            content: the content of the note 
        Returns:
            the Note instance representing the created note
        """
        note = Note(
            id = str(uuid.uuid4()),
            creation_time = now(),
            author_id = author.user_id, 
            type = NoteType.FREE,
            tags = tags or []
        )

        self.bucket_adapter.store(
            self._get_object_key_for_note(note.id),
            content.strip()
        )

        self.note_repository.save(note)
        
        return note

    def find_note_by_id(self, note_id: str) -> Note:
        """
        Returns a note by its id, based on Markdown standard.
    
        Args:
            note_id: the id of the wanted note
        Returns:
            the Note instance matching the required id

        Throws:
            a ResourceNotFoundException if there is not such note
        """
        note = self.note_repository.find_by_id(note_id)
        if not note:
            raise ResourceNotFoundException("Note", note_id)
        return note

    def delete_note_by_id(self, note_id: str) -> Note:
        """
        Deletes a note with the specified id, if present.
    
        Args:
            note_id: the id of the wanted note
        Returns:
            nothing
        """
        self.note_repository.delete_by_id(note_id)

        self.bucket_adapter.delete(
            self._get_object_key_for_note(note_id)
        )

    def _get_object_key_for_note(self, note_id: str) -> str:
        return f"notes/{note_id}.md"
