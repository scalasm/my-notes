# pylint: disable=redefined-outer-name
from pathlib import Path

import os
import pytest

from moto import mock_s3, mock_dynamodb2
import boto3

@pytest.fixture(scope='function')
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

@pytest.fixture(scope='function')
def s3_resource(aws_credentials):
    with mock_s3():
        yield boto3.resource("s3", region_name="us-east-1")

@pytest.fixture(scope='function')
def dynamodb_resource(aws_credentials):
    with mock_dynamodb2():
        yield boto3.resource("dynamodb", region_name="us-east-1")