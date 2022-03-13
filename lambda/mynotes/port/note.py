import json

import boto3
from mynotes.adapter.config import NOTES_CONTENT_BUCKET_NAME
from mynotes.adapter.notes_adapter import DynamoDBNoteRepository
from mynotes.adapter.s3_bucket_adapter import S3BucketAdapter
from mynotes.core.architecture import User
from mynotes.core.notes import NoteUseCases
from mynotes.port import lambda_utils
from mynotes.port.exception_management import with_exception_management

object_store = S3BucketAdapter(
    boto3.resource("s3"),
    NOTES_CONTENT_BUCKET_NAME
)

note_repository = DynamoDBNoteRepository()

usecase = NoteUseCases(object_store, note_repository)

@with_exception_management
def handler_create_note(event, context) -> dict:
    """Handler for creating a new note.
    Args:
        event: the AWS Lambda event
        context: the AWS Lambda execution context
    
    Returns:
        a dict suitable as AWS Lambda response
    """
    print(json.dumps(event))

    json_body = lambda_utils.get_json_body(event)
    id = json_body.get("id", None)
    content = json_body.get("content")    
    tags = json_body.get("tags", None)

    # TODO Get user from authentication
    username = "mario"

    note = usecase.create_note(
        User(username),
        content,
        tags
    )

    return lambda_utils.to_json_response(note)

@with_exception_management
def handler_get_by_id(event, context) -> dict:
    """Handler for returning a note by its id.
    Args:
        event: the AWS Lambda event
        context: the AWS Lambda execution context
    
    Returns:
        a dict suitable as AWS Lambda response
    """
    print(json.dumps(event))

    id = lambda_utils.get_path_parameter("id")

    note = usecase.find_note_by_id(id)

    return lambda_utils.to_json_response(note)

@with_exception_management
def handler_delete_by_id(event, context) -> dict:
    """Handler for deleting a note.
    Args:
        event: the AWS Lambda event
        context: the AWS Lambda execution context
    
    Returns:
        a dict suitable as AWS Lambda response
    """
    print(json.dumps(event))

    id = lambda_utils.get_path_parameter("id")

    usecase.delete_note_by_id(id)

    return {
        "status": 204
    }

