import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List

from mynotes.core.architecture import (DomainEntity, ObjectStore, User,
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

    """Entity class representing metadata associated to a Note entity"""
    def __init__(self, author_id: str, type: NoteType, creation_time: datetime, tags: List[str] = None, id: str = None) -> None:
        super().__init__(id)
        self.author_id = author_id
        self.creation_time = creation_time
        self.type = type
        self.tags = tags or {}

class NoteRepository(ABC):
    @abstractmethod
    def save(self, note: Note) -> None:
        pass

    @abstractmethod
    def get_by_id(self, id: str) -> None:
        pass

@wrap_exceptions
class CreateNoteUseCase:
    bucket_adapter: ObjectStore
    note_repository: NoteRepository

    def __init__(self, bucket_adapter: ObjectStore, note_repository: NoteRepository) -> None:
        self.bucket_adapter = bucket_adapter
        self.note_repository = note_repository

    def create_note(self, author: User, content: str) -> Note:
        note = Note(
            id = str(uuid.uuid4()),
            creation_time = now(),
            author_id = author.user_id, 
            type = NoteType.FREE,
            tags = ["note"]
        )

        content = content.strip()

        object_key = f"notes/{note.id}.md"

        self.bucket_adapter.store(object_key, content)

        self.note_repository.save(note)
        
        return note

    def get_note_by_id(self, note_id: str) -> Note:
        return self.note_repository.get_by_id(note_id)
