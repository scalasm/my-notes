import os 
from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute, UnicodeSetAttribute
from pynamodb.models import Model

from mynotes.core.notes import Note, NoteRepository, NoteType
from mynotes.adapter.config import NOTES_TABLE_NAME, LOCALSTACK_ENDPOINT, AWS_REGION

class NoteModel(Model):
    """DynamoDB model for Notes"""
    class Meta:
        region = AWS_REGION
        table_name = NOTES_TABLE_NAME

    if LOCALSTACK_ENDPOINT:
        setattr(Meta, "host", LOCALSTACK_ENDPOINT)

    id = UnicodeAttribute(hash_key = True)

    creation_time = UTCDateTimeAttribute()
    author_id = UnicodeAttribute()
    type = UnicodeAttribute()
    tags = UnicodeSetAttribute()

class DynamoDBNoteRepository(NoteRepository):
    def save(self, note: Note) -> None:
        note_model = map_to_note_model(note)
        
        note_model.save()

    def get_by_id(self, id: str) -> Note:
        note_model = NoteModel.get(id)

        return map_to_note(note_model)

def map_to_note_model(note: Note) -> NoteModel:
    model = NoteModel(
        id = note.id,
        creation_time = note.creation_time
    )
    model.author_id = note.author_id
    model.type = note.type.value
    model.tags = set(note.tags)

    return model

def map_to_note(note_model: NoteModel) -> Note:
    return Note(
        id = note_model.id,
        type=NoteType(note_model.type),
        creation_time = note_model.creation_time,
        tags=list(note_model.tags),
        author_id=note_model.author_id
    )
