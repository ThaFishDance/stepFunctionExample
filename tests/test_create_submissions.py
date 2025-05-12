import json
import os
import zipfile
import io
import base64
import boto3
import functions.create_submissions.app as app
from moto import mock_aws
import pytest
from dotenv import load_dotenv
load_dotenv()


@mock_aws
def test_square_number_lambda_creates_zip_and_uploads_to_s3():
    count = 5  # how many inner ZIPs we want
    bucket = os.getenv("BUCKET_NAME")
    key = "nested/outer_result.zip"
    json_count = 3
    number = 10


    # Setup mock S3
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket=bucket)

    # Prepare event
    event = {
        "number": 10,
        "name1": "Alice",
        "name2": "Bob",
        "count": count,
        "json_count": json_count,
        # 'key': "nested/outer_result.zip"
    }

    # Run Lambda
    result = app.lambda_handler(event, {})

    # Validate result
    assert result["message"] == f"{count} inner ZIPs uploaded successfully"
    assert result["s3_bucket"] == bucket
    assert result["s3_key"] == key

    # Download and inspect the outer ZIP from S3
    obj = s3.get_object(Bucket=bucket, Key=key)
    outer_zip_bytes = obj["Body"].read()
    outer_zip = zipfile.ZipFile(io.BytesIO(outer_zip_bytes))

    inner_zip_names = outer_zip.namelist()
    assert len(inner_zip_names) == count

    for i in range(count):
        expected_name = f"inner_result_{i}.zip"
        assert expected_name in inner_zip_names

        # Check contents of each inner ZIP
        inner_zip_bytes = outer_zip.read(expected_name)
        inner_zip = zipfile.ZipFile(io.BytesIO(inner_zip_bytes))
        inner_file_names = inner_zip.namelist()
        assert len(inner_file_names) == json_count

        for j in range(json_count):
            json_name = f"result{i}_{j}.json"
            assert json_name in inner_file_names

            data = json.loads(inner_zip.read(json_name).decode("utf-8"))
            expected_number = number + i + j
            assert data["number"] == expected_number
            assert data["square"] == expected_number ** 2
            assert data["processed_by"] == ["Alice", "Bob"]