from ast import Global
from datetime import datetime
import logging
from typing import List
from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute, UnicodeSetAttribute, VersionAttribute, NumberAttribute
from pynamodb.models import Model
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection

from mynotes.core.architecture import DataPage, DataPageQuery
from mynotes.adapter.utils import encode_dict_to_base64, decode_str_as_dict
from mynotes.core.notes import Note, NoteRepository, NoteType
from mynotes.adapter.config import NOTES_TABLE_NAME, LOCALSTACK_ENDPOINT, AWS_REGION
import json
import base64

# Identifier for notes that are public, not belonging to any specific user.
PUBLIC_AUTHOR_ID = "__PUBLIC__"
# Max amount of data page that will be returned by query responses
DEFAULT_DATA_PAGE_LIMIT = 10

class NoteModelSearchByAuthorAndTypeIndex(GlobalSecondaryIndex):
    """
    DynamodDB GSI that supports queries by author and type for notes.
    """
    class Meta:
        index_name = "SearchByAuthorAndTypeIndex"
        # You can override the index name by setting it below
        read_capacity_units = 1
        write_capacity_units = 1
        # All attributes are projected
        projection = AllProjection()
        region = AWS_REGION

    author_id_and_type = UnicodeAttribute(hash_key = True)
    creation_time = UTCDateTimeAttribute(range_key = True)  

class NoteModel(Model):
    """
    DynamoDB model for Notes
    """
    class Meta:
        region = AWS_REGION
        table_name = NOTES_TABLE_NAME

    if LOCALSTACK_ENDPOINT:
        setattr(Meta, "host", LOCALSTACK_ENDPOINT)

    id = UnicodeAttribute(hash_key = True)

    creation_time = UTCDateTimeAttribute()
    # Format: <USER_ID>#<NOTE_TYPE>
    author_id_and_type = UnicodeAttribute()
    tags = UnicodeSetAttribute()
    version = VersionAttribute(null=True)

    search_by_author_and_type_index = NoteModelSearchByAuthorAndTypeIndex()


def map_to_note_model(note: Note) -> NoteModel:
    model = NoteModel(
        id = note.id,
        creation_time = note.creation_time
    )
    model.author_id_and_type = f"{note.author_id}#{note.type.value}"
    model.tags = set(note.tags) if note.tags else {}
    if note.version:
        model.version = note.version

    return model

def map_to_note(note_model: NoteModel) -> Note:
    author_id, note_type = note_model.author_id_and_type.split("#")

    return Note(
        id = note_model.id,
        type = NoteType(note_type),
        creation_time = note_model.creation_time,
        tags = list(note_model.tags) if note_model.tags else list(),
        author_id = author_id,
        version = note_model.version
    )

class DynamoDBNoteRepository(NoteRepository):
    def save(self, note: Note) -> None:
        note_model = map_to_note_model(note)
        
        note_model.save()

    def find_by_id(self, id: str) -> Note:
        try:
            note_model = NoteModel.get(id)

            return map_to_note(note_model)
        except NoteModel.DoesNotExist:
            logging.debug(f"Note with id {id} was not found!")
            return None

    def delete_by_id(self, id: str) -> None:
        try:
            # XXX Review this implementation - I should not need to do 
            # a "get" before a "delete" :|
            note_model = NoteModel.get(id)
            note_model.delete()
#            note_model.delete(NoteModel.id == id)
        except NoteModel.DoesNotExist:
            logging.debug(f"Note with id {id} was not found!")

    def find_all_by_type(self, note_type: NoteType, author_id: str = None, data_page_query: DataPageQuery = None) -> DataPage[Note]:
        author_id = author_id or PUBLIC_AUTHOR_ID
        pk = f"{author_id}#{note_type.value}"

        page_size = data_page_query.page_size if data_page_query else DEFAULT_DATA_PAGE_LIMIT
        continuation_token = data_page_query.continuation_token if data_page_query else None

        page_results = NoteModel.search_by_author_and_type_index.query(
            pk, 
#            NoteModelSearchByAuthorAndTypeIndex.creation_time > datetime(2008, 8, 12, 12, 20, 30, 656234),
            limit=page_size,
            last_evaluated_key=decode_str_as_dict(continuation_token)
        )

        items = [map_to_note(item) for item in page_results]
        n_items = len(items)

        continuation_token = encode_dict_to_base64(page_results.last_evaluated_key) if page_results.last_evaluated_key else None

        return DataPage(
            items,
            n_items,
            continuation_token 
        )
