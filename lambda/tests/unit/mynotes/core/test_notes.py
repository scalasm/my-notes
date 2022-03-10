import pytest
from mynotes.core.architecture import ObjectStore, User
from mynotes.core.notes import (CreateNoteUseCase, Note, NoteRepository,
                                NoteType)
from pytest_mock import MockerFixture


@pytest.fixture
def mock_bucket_adapter(mocker: MockerFixture) -> ObjectStore:
    return mocker.Mock(spec=ObjectStore)

@pytest.fixture
def mock_note_repository(mocker: MockerFixture) -> NoteRepository:
    return mocker.Mock(spec=NoteRepository)

@pytest.fixture
def usecase(mock_bucket_adapter: ObjectStore, mock_note_repository: NoteRepository) -> CreateNoteUseCase:
    return CreateNoteUseCase(mock_bucket_adapter, mock_note_repository)

class TestCreateNoteUseCase:

    def test_create_note(self, 
        usecase: CreateNoteUseCase, 
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
