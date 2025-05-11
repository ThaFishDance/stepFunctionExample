import boto3
import uuid
import pytest
from dotenv import load_dotenv
import os
from moto import mock_aws

load_dotenv()


@pytest.fixture
def moto_s3_bucket():
    bucket_name = os.getenv("BUCKET_NAME", None)

    with mock_aws():
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket=bucket_name)
        yield {
            "client": s3,
            "bucket": bucket_name
        }
