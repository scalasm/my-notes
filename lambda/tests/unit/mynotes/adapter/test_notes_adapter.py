from datetime import datetime, timezone
from ensurepip import version
from typing import Any, List, Set
from xmlrpc.client import Boolean

import pytest
from mynotes.adapter.notes_adapter import (DynamoDBNoteRepository, NoteModel,
                                           map_to_note, map_to_note_model)
from mynotes.core.notes import Note, NoteType

SAMPLE_NOTE_TEXT = """
    # This is a test
    Watch out people, I can write markdown into S3 bucket!
    ## Section 1
    This is a section
    ## Section 2 
    Another section
    # Misc
    * Point 1
    * Point 2
    * Point 3
    """

@pytest.fixture
def notes_table(dynamodb_resource: Any) -> str:
    NoteModel.create_table(
        wait = True,
        read_capacity_units=1, write_capacity_units=1
    )
    return "test-notes-table"

@pytest.fixture
def note_repository(notes_table: str) -> DynamoDBNoteRepository:
    return DynamoDBNoteRepository()

class TestDynamoDBNoteRepository:
    def test_create_note(self, note_repository: DynamoDBNoteRepository) -> None:
        note = Note(
            author_id = "mario",
            type = NoteType.FREE,
            creation_time = datetime.now(timezone.utc),
            tags = ["test"]
        )

        note_repository.save(note)
        
        self._assert_note_exists(note.id)

    def test_find_by_id_existing_note(self, note_repository: DynamoDBNoteRepository) -> None:
        existing_note_model = self._create_test_note_model()

        note_from_db = note_repository.find_by_id(existing_note_model.id)
        
        assert note_from_db.id == existing_note_model.id
        assert note_from_db.author_id == existing_note_model.author_id
        assert note_from_db.creation_time == existing_note_model.creation_time
        assert note_from_db.tags == list(existing_note_model.tags)
        assert note_from_db.type == NoteType(existing_note_model.type)
        assert note_from_db.version == existing_note_model.version


    def test_find_by_id_not_existing_note(self, note_repository: DynamoDBNoteRepository) -> None:
        note_from_db = note_repository.find_by_id("not-existing-id")
        assert note_from_db == None

    def test_delete_by_id_existing_note(self, note_repository: DynamoDBNoteRepository) -> None:
        existing_note = self._create_test_note_model()

        note_repository.delete_by_id(existing_note.id)

        self._assert_note_does_not_exist(existing_note.id)

    def test_delete_by_id_not_existing_note(self, note_repository: DynamoDBNoteRepository) -> None:
        note_repository.delete_by_id("not-existing-id")
        # No errors - delete will delete if item is present or do nothing if item is not present
        assert True

    def _create_test_note_model(self, id: str = None, author_id: str = None, note_type: str = None, creation_time: datetime = None, tags: Set[str] = None) -> NoteModel:
        note_model = NoteModel(
            id = id or "1",
            author_id = author_id or "mario",
            type = note_type or "F",
            creation_time = creation_time or datetime.now(timezone.utc),
            tags = tags or {"test"}
        )

        note_model.save()

        return note_model

    def _assert_note_exists(self, note_id: str) -> None:
        assert self._is_note_present(note_id), f"Note with di {note_id} was not found in table!"

    def _assert_note_does_not_exist(self, note_id: str) -> None:
        assert not self._is_note_present(note_id), f"Note with di {note_id} is still in table!"

    def _is_note_present(self, note_id: str) -> Boolean:
        item_is_present = True
        try:
            NoteModel.get(note_id)
        except NoteModel.DoesNotExist:
            item_is_present = False
        return item_is_present

def test_map_to_note_model() -> None:
    note = Note(
        id = "1",
        author_id = "mario",
        type = NoteType.FREE,
        creation_time = datetime.now(timezone.utc),
        tags = ["test"],
        version = 2
    )

    note_model = map_to_note_model(note)

    assert note_model.id == "1"
    assert note_model.author_id == "mario"
    assert note_model.type == "F"
    assert note_model.creation_time == note.creation_time
    assert note_model.tags == set(note.tags)
    assert note_model.version == 2

def test_map_to_note() -> None:
    note_model = NoteModel(
        id = "1",
        author_id = "mario",
        type = "F",
        creation_time = datetime.now(timezone.utc),
        tags = {"test"},
        version = 2
    )

    note = map_to_note(note_model)

    assert note.id == "1"
    assert note.author_id == "mario"
    assert note.type == NoteType.FREE
    assert note.creation_time == note.creation_time
    assert note.tags == ["test"]
    assert note.version == 2
