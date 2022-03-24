from ensurepip import version
import logging
import os
from datetime import datetime, timezone
from typing import Any, List, Set
from xmlrpc.client import boolean

from unit.mynotes.adapter.custom_boto3_mocks import aws_credentials, dynamodb_resource

#os.environ["LOCALSTACK_ENDPOINT"] = "http://0.0.0.0:4566"
#from unit.mynotes.adapter.custom_boto3_localstack import aws_credentials, dynamodb_resource

import pytest
from mynotes.core.architecture import DataPage, DataPageQuery
from mynotes.adapter.notes_adapter import (PUBLIC_AUTHOR_ID, DynamoDBNoteRepository, NoteModel,
                                           map_to_note, map_to_note_model)
from mynotes.core.notes import Note, NoteType

logging.basicConfig()
log = logging.getLogger("pynamodb")
log.setLevel(logging.DEBUG)
log.propagate = True

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

@pytest.yield_fixture(scope="class")
def notes_table(dynamodb_resource: Any) -> str:
    """Create/destroy the table along this entire test suite"""
    if not NoteModel.exists():
        NoteModel.create_table(
            wait = True,
            read_capacity_units=1, write_capacity_units=1
        )
    yield "test-notes-table"

    # Clean up After all tests
    NoteModel.delete_table()

@pytest.fixture
def note_repository(notes_table: str) -> DynamoDBNoteRepository:
    return DynamoDBNoteRepository()

@pytest.fixture()
def notes_table_data_cleaner(notes_table: str) -> str:
    """Ensure that table is clean before running the test"""
    for item in NoteModel.scan():
        item.delete()
    return "notes_table_data_cleaner"

class TestDynamoDBNoteRepository:
    def test_create_note(self, note_repository: DynamoDBNoteRepository) -> None:
        note = Note(
            author_id = "mario",
            type = NoteType.FREE,
            creation_time = datetime.now(timezone.utc),
            tags = ["test"]
        )

        note_repository.save(note)

        # This whould throw a NotFound exception if the note is not in table        
        note_model = NoteModel.get(note.id)
        assert note_model.tags == {"test"}

    def test_create_note_without_tags(self, note_repository: DynamoDBNoteRepository) -> None:
        note = Note(
            author_id = "mario",
            type = NoteType.FREE,
            creation_time = datetime.now(timezone.utc),
            # No tags
        )

        note_repository.save(note)
        
        note_model = NoteModel.get(note.id)
        # There are no tags (note_model.tags is none)
        assert not note_model.tags

    def test_find_by_id_existing_note(self, note_repository: DynamoDBNoteRepository) -> None:
        existing_note_model = _create_test_note_model_in_table(
            author_id="mario"
        )

        note_from_db = note_repository.find_by_id(existing_note_model.id)
        
        assert note_from_db.id == existing_note_model.id
        assert note_from_db.author_id == "mario"
        assert note_from_db.creation_time == existing_note_model.creation_time
        assert note_from_db.tags == list(existing_note_model.tags)
        assert note_from_db.type == NoteType.FREE
        assert note_from_db.version == existing_note_model.version

    def test_find_by_id_not_existing_note(self, note_repository: DynamoDBNoteRepository) -> None:
        note_from_db = note_repository.find_by_id("not-existing-id")
        assert note_from_db == None

    def test_delete_by_id_existing_note(self, note_repository: DynamoDBNoteRepository, notes_table_data_cleaner: Any) -> None:
        items = [item for item in NoteModel.scan()]
        existing_note = _create_test_note_model_in_table()

        note_repository.delete_by_id(existing_note.id)

        self._assert_note_does_not_exist(existing_note.id)

    def test_delete_by_id_not_existing_note(self, note_repository: DynamoDBNoteRepository) -> None:
        note_repository.delete_by_id("not-existing-id")
        # No errors - delete will delete if item is present or do nothing if item is not present
        assert True

    def _assert_note_exists(self, note_id: str) -> None:
        assert self._is_note_present(note_id), f"Note with di {note_id} was not found in table!"

    def _assert_note_does_not_exist(self, note_id: str) -> None:
        assert not self._is_note_present(note_id), f"Note with di {note_id} is still in table!"

    def _is_note_present(self, note_id: str) -> bool:
        item_is_present = True
        try:
            NoteModel.get(note_id)
        except NoteModel.DoesNotExist:
            item_is_present = False
        return item_is_present


@pytest.yield_fixture(scope="function")
def test_notes(notes_table: Any) -> str:
    """"Create some test data in the database and clean them up after the test executed"""
    test_notes_data_set = [
        _create_test_note_model_in_table(id="10", note_type="Q"),
        _create_test_note_model_in_table(id="11", note_type="Q"),
        _create_test_note_model_in_table(id="12", note_type="Q"),
        _create_test_note_model_in_table(id="20", note_type="F")
    ]

    yield test_notes_data_set

    # Clean up (no quicker way?)
    for item in NoteModel.scan():
        item.delete()

class TestDynamoDBNoteRepositoryQueries:
    """Test access patterns on the main table"""
    test_find_all_by_type_test_data = [
        (NoteType.QUESTION, 3),
        (NoteType.FREE, 1),
        (NoteType.INTERVIEW, 0)
    ]

    @pytest.mark.parametrize("note_type,expected_n_items", test_find_all_by_type_test_data)
    def test_find_all_by_type(self, note_type: NoteType, expected_n_items: int, note_repository: DynamoDBNoteRepository, test_notes: List[NoteModel]) -> None:
        assert note_repository.find_all_by_type(note_type).page_size == expected_n_items

    test_find_all_by_type_using_custom_page_size_test_data = [
        (NoteType.QUESTION, DataPageQuery(page_size=1), 1, True),
        (NoteType.QUESTION, DataPageQuery(page_size=10), 3, False),
        (NoteType.QUESTION, None, 3, False)
    ]

    @pytest.mark.parametrize("note_type,data_page_query,expected_n_items,expected_continuation_token_set", test_find_all_by_type_using_custom_page_size_test_data)
    def test_find_all_by_type_using_custom_page_size(self, note_type: NoteType, data_page_query: DataPageQuery, expected_n_items: int, expected_continuation_token_set: boolean, note_repository: DynamoDBNoteRepository, test_notes: List[NoteModel]) -> None:
        data_page = note_repository.find_all_by_type(note_type, data_page_query=data_page_query)
        assert data_page.page_size == expected_n_items

        is_continuation_token_set = not data_page.continuation_token == None
        assert is_continuation_token_set == expected_continuation_token_set

def _create_test_note_model(id: str = None, author_id: str = None, note_type: str = None, creation_time: datetime = None, tags: Set[str] = None) -> NoteModel:
    author_id = author_id or PUBLIC_AUTHOR_ID
    note_type = note_type or "F"

    note_model = NoteModel(
        id = id or "1",
        author_id_and_type = f"{author_id}#{note_type}",
        creation_time = creation_time or datetime.now(timezone.utc),
        tags = tags or {"test"}
    )

    return note_model

def _create_test_note_model_in_table(id: str = None, author_id: str = None, note_type: str = None, creation_time: datetime = None, tags: Set[str] = None) -> NoteModel:
    note_model = _create_test_note_model(
        id=id, author_id=author_id, note_type=note_type, creation_time=creation_time, tags=tags
    )

    note_model.save()

    return note_model

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
    assert note_model.author_id_and_type == f"mario#F"
    assert note_model.creation_time == note.creation_time
    assert note_model.tags == set(note.tags)
    assert note_model.version == 2

def test_map_to_note() -> None:
    note_model = NoteModel(
        id = "1",
        author_id_and_type = "mario#F",
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

def test_map_to_note_no_tags_should_map_to_empty_array() -> None:
    note_model = NoteModel(
        id = "1",
        author_id_and_type = "mario#F",
        creation_time = datetime.now(timezone.utc),
        tags = None,
        version = 2
    )

    note = map_to_note(note_model)

    # We only want to be sure that if "tags" attribute is None,
    # then we get an empty list for tags 
    assert note.tags == []
