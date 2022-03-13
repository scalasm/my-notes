from typing import Any
from mynotes.core.architecture import ContentUploadException, ObjectStore

class S3BucketAdapter(ObjectStore):
    """
        Adapter implementation for the S3 object store.
    """
    bucket_name: str
    s3_resource: Any

    def __init__(self, s3_resource: Any, bucket_name: str) -> None:
        self.s3_resource = s3_resource
        self.bucket_name = bucket_name

    def store(self, object_key: str, content: str) -> None:
        object = self.s3_resource.Object(self.bucket_name, object_key)

        result = object.put(Body=content)

        res = result.get('ResponseMetadata')
        if not res.get('HTTPStatusCode') == 200:
            raise ContentUploadException(f"Upload to bucket {self.bucket_name} failed for key {object_key}!")

    def load(self, object_key: str) -> str:
        object = self.s3_resource.Object(self.bucket_name, object_key)
        content = object.get()['Body'].read().decode('utf-8')

        return content

    def delete(self, object_key: str) -> None:
        object = self.s3_resource.Object(self.bucket_name, object_key)
        # We don't care about the response - either the object was deleted (if present)
        # or it was not present!
        object.delete()

