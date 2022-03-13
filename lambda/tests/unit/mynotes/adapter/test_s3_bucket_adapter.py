from typing import Any
import pytest
from botocore.errorfactory import ClientError

from mynotes.adapter.s3_bucket_adapter import S3BucketAdapter

TEST_BUCKET = "my-tests"

@pytest.fixture
def bucket_adapter(s3_resource: Any) -> S3BucketAdapter:
    return S3BucketAdapter(s3_resource, TEST_BUCKET)

@pytest.fixture
def s3_bucket(s3_resource: Any) -> Any:
    bucket = s3_resource.Bucket(TEST_BUCKET)
    bucket.create()

    return bucket

class TestS3BucketAdapter:

    def test_store(self, bucket_adapter: S3BucketAdapter, s3_resource: Any, s3_bucket: Any) -> None:
        key = "test.md"
        content = "Some content"

        bucket_adapter.store(key, content)

        _assert_content_for_object_key(s3_resource, key, content)

    def test_store_overwrite_existing_content(self, bucket_adapter: S3BucketAdapter, s3_resource: Any, s3_bucket: Any) -> None:
        key = "test.md"

        bucket_adapter.store(key, "First content")

        bucket_adapter.store(key, "Second content")

        _assert_content_for_object_key(s3_resource, key, "Second content")

    def test_load(self, bucket_adapter: S3BucketAdapter, s3_resource: Any, s3_bucket: Any) -> None:
        key = "test.md"
        content = "Some content"

        object = s3_resource.Object(TEST_BUCKET, key)
        object.put(Body = content)

        content_from_bucket = bucket_adapter.load(key)

        assert content_from_bucket == content 


    def test_delete_not_existing_key_is_fine(self, bucket_adapter: S3BucketAdapter, s3_resource: Any, s3_bucket: Any) -> None:
        bucket_adapter.delete("not-existing-key")
        # No errors, it is fine!
        assert True

    def test_delete(self, bucket_adapter: S3BucketAdapter, s3_resource: Any, s3_bucket: Any) -> None:
        key = "test.md"
        content = "Some content"

        object = s3_resource.Object(TEST_BUCKET, key)
        object.put(Body = content)

        bucket_adapter.delete(key)

        _assert_object_is_not_present(s3_resource, key)

def _assert_content_for_object_key(s3_resource: Any, object_key: str, expected_content: str) -> None:
    object = s3_resource.Object(TEST_BUCKET, object_key)
    content_from_bucket = object.get()['Body'].read().decode('utf-8')

    assert content_from_bucket == expected_content

def _assert_object_is_not_present(s3_resource: Any, object_key: str) -> None:
    object = s3_resource.Object(TEST_BUCKET, object_key)

    object_is_here = True
    try: 
        object.get()
    except ClientError:
        object_is_here = False
    
    return object_is_here