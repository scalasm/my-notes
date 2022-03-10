import os

# Stack region - This is set directly by AWS
AWS_REGION = os.getenv("AWS_REGION", "eu-west-1")

# DynamoDB used for storing the note metadata 
NOTES_TABLE_NAME = os.getenv("NOTES_TABLE_NAME", "Notes")
NOTES_CONTENT_BUCKET_NAME = os.getenv("NOTES_CONTENT_BUCKET_NAME", "NotesContent")

# Localstack endpoint, if available
LOCALSTACK_ENDPOINT = os.getenv("LOCALSTACK_ENDPOINT", None)
