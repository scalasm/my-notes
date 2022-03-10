from datetime import datetime, timezone
from typing import Any, List

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
            "mario",
            NoteType.FREE,
            datetime.now(timezone.utc),
            ["test"]
        )

        note_repository.save(note)
        
        model_from_db = NoteModel.get(note.id)

        assert not model_from_db.id == None

    def test_find_by_id(self, note_repository: DynamoDBNoteRepository) -> None:
        note_model = NoteModel(
            id = "1",
            author_id = "mario",
            type = "F",
            creation_time = datetime.now(timezone.utc),
            tags = {"test"}
        )

        note_model.save()

        note_from_db = note_repository.get_by_id("1")

        assert not note_from_db.id == None


def test_map_to_note_model() -> None:
    note = Note(
        id = "1",
        author_id = "mario",
        type = NoteType.FREE,
        creation_time = datetime.now(timezone.utc),
        tags = ["test"]
    )

    note_model = map_to_note_model(note)

    assert note_model.id == "1"
    assert note_model.author_id == "mario"
    assert note_model.type == "F"
    assert note_model.creation_time == note.creation_time
    assert note_model.tags == set(note.tags)

def test_map_to_note() -> None:
    note_model = NoteModel(
        id = "1",
        author_id = "mario",
        type = "F",
        creation_time = datetime.now(timezone.utc),
        tags = {"test"}
    )

    note = map_to_note(note_model)

    assert note.id == "1"
    assert note.author_id == "mario"
    assert note.type == NoteType.FREE
    assert note.creation_time == note.creation_time
    assert note.tags == ["test"]
