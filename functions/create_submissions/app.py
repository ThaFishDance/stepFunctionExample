import json
import io
import os
import zipfile
import boto3
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

load_dotenv()

BUCKET_NAME = os.getenv("BUCKET_NAME")


def create_inner_zip(index, number, name1, name2, json_count=1):
    inner_zip_buffer = io.BytesIO()
    with zipfile.ZipFile(inner_zip_buffer, 'w', zipfile.ZIP_DEFLATED) as inner_zip:
        for j in range(json_count):
            result_data = {
                "number": number + index + j,
                "square": (number + index + j) ** 2,
                "processed_by": [name1, name2]
            }
            inner_zip.writestr(f"result{index}_{j}.json", json.dumps(result_data).encode("utf-8"))
    inner_zip_buffer.seek(0)
    return f"inner_result_{index}.zip", inner_zip_buffer.read()


def get_s3_key(number):
    return "nested/outer_result.zip"


def lambda_handler(event, context):
    s3 = boto3.client("s3")
    number = event["number"]
    KEY_NAME = get_s3_key(number)
    name1 = event["job_id"]
    count = int(event.get("count", 1))  # default to 1 if not provided
    json_count = int(event.get("json_count", 1))
    print(f'test count: {count}')

    inner_zip_results = []
    with ThreadPoolExecutor(max_workers=3) as executor:  # max 3 concurrent workers
        futures = [
            executor.submit(create_inner_zip, i, number, name1, name2, json_count)
            for i in range(count)
        ]
        for future in futures:
            inner_zip_results.append(future.result())

    print(len(inner_zip_results))

    outer_zip_buffer = io.BytesIO()
    with zipfile.ZipFile(outer_zip_buffer, 'w', zipfile.ZIP_DEFLATED) as outer_zip:
        for zip_name, zip_bytes in inner_zip_results:
            outer_zip.writestr(zip_name, zip_bytes)
    outer_zip_buffer.seek(0)

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=KEY_NAME,
        Body=outer_zip_buffer.getvalue(),
        ContentType="application/zip"
    )

    return {
        "message": f"{len(inner_zip_results)} inner ZIPs uploaded successfully",
        "s3_bucket": BUCKET_NAME,
        "s3_key": KEY_NAME
    }
