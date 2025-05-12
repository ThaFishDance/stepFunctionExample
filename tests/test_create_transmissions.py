# test_create_transmissions.py

import functions.create_transmissions.app as app  # adjust this path if needed


def test_lambda_handler_creates_csv_and_uploads_to_s3(moto_s3_bucket):
    # Set BUCKET_NAME from the fixture
    bucket_name = moto_s3_bucket["bucket"]

    # Run Lambda handler
    event = {}
    result = app.lambda_handler(event, {})

    # Validate the return structure
    assert "numbers" in result
    assert result["numbers"] == [0, 1, 2]  # One transmission per doc_code × 3 codes

    # Check uploaded CSV in S3
    s3 = moto_s3_bucket["client"]
    response = s3.list_objects(Bucket=bucket_name)
    assert "Contents" in response

    csv_keys = [obj["Key"] for obj in response["Contents"] if obj["Key"].endswith(".csv")]
    assert len(csv_keys) == 1

    # Optional: Validate CSV contents
    csv_obj = s3.get_object(Bucket=bucket_name, Key=csv_keys[0])
    csv_lines = csv_obj["Body"].read().decode("utf-8").strip().split("\r\n")
    assert csv_lines[0] == "TransmissionName"
    assert sorted(csv_lines[1:]) == sorted(["CI_dc1_0", "CI_dc2_0", "CI_dc3_0"])