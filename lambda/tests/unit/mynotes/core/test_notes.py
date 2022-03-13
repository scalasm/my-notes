import pytest
from mynotes.core.architecture import ObjectStore, ResourceNotFoundException, User
from mynotes.core.notes import (NoteUseCases, Note, NoteRepository,
                                NoteType)
from pytest_mock import MockerFixture


@pytest.fixture
def mock_bucket_adapter(mocker: MockerFixture) -> ObjectStore:
    return mocker.Mock(spec=ObjectStore)

@pytest.fixture
def mock_note_repository(mocker: MockerFixture) -> NoteRepository:
    return mocker.Mock(spec=NoteRepository)

@pytest.fixture
def usecase(mock_bucket_adapter: ObjectStore, mock_note_repository: NoteRepository) -> NoteUseCases:
    return NoteUseCases(mock_bucket_adapter, mock_note_repository)

class TestNoteUseCases:

    def test_create_note(self, 
        usecase: NoteUseCases, 
        mock_bucket_adapter: ObjectStore, mock_note_repository: NoteRepository) -> None:
        content = """
    #This is a title
    This is a test content that we want to write using **Markdown** formatting.

    ##Sub-title
    We can write standard markdown without any problem
        """.strip()

        note = usecase.create_note(
            User("mario"),
            content
        )

        mock_bucket_adapter.store.assert_called_once_with(f"notes/{note.id}.md", content)

        mock_note_repository.save.assert_called_once()

    def test_find_note_by_id_must_throw_exception_if_note_does_not_exist(self, 
        usecase: NoteUseCases, 
        mock_bucket_adapter: ObjectStore, mock_note_repository: NoteRepository) -> None:

        mock_note_repository.find_by_id.return_value = None

        with pytest.raises(ResourceNotFoundException):
            usecase.find_note_by_id("some-id")

    def test_find_note_by_id(self, 
        usecase: NoteUseCases, 
        mock_bucket_adapter: ObjectStore, mock_note_repository: NoteRepository) -> None:

        test_note = Note(id="test-id", author_id="test-user")

        mock_note_repository.find_by_id.return_value = test_note

        found_note = usecase.find_note_by_id("test-id")

        mock_note_repository.find_by_id.assert_called_once_with("test-id")
        assert found_note == test_note

    def test_delete_note_by_id(self, 
        usecase: NoteUseCases, 
        mock_bucket_adapter: ObjectStore, mock_note_repository: NoteRepository) -> None:

        usecase.delete_note_by_id("test-id")

        mock_note_repository.delete_by_id.assert_called_once_with("test-id")
        
        mock_bucket_adapter.delete.assert_called_once_with("notes/test-id.md")