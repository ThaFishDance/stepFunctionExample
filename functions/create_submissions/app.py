import json
import io
import os
import zipfile
import boto3
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

load_dotenv()

BUCKET_NAME = os.getenv("BUCKET_NAME")


def create_inner_zip(index, doc_code, json_count=1):
    inner_zip_buffer = io.BytesIO()
    with zipfile.ZipFile(inner_zip_buffer, 'w', zipfile.ZIP_DEFLATED) as inner_zip:
        for j in range(json_count):
            result_data = {
                "doc_code": doc_code
            }
            inner_zip.writestr(f"result_{index}_{j}.json", json.dumps(result_data).encode("utf-8"))
    inner_zip_buffer.seek(0)
    return f"inner_result_{index}.zip", inner_zip_buffer.read()


def get_s3_key(job_id, number):
    # TODO: get csv from s3, the s3 key is the job_id
    #  and row data from row[number]
    return "nested/outer_result.zip"


def lambda_handler(event, context):
    s3 = boto3.client("s3")
    number = event["number"] # comes from the map item value
    job_id = event["job_id"]
    transmission_zip_name = get_s3_key(job_id, number)
    submission_count = int(event.get("submission_count", 1))  # default to 1 if not provided
    json_count = int(event.get("json_count", 1))
    print(f'submission_count: {submission_count}')

    inner_zip_results = []
    with ThreadPoolExecutor(max_workers=3) as executor:  # max 3 concurrent workers
        futures = [
            executor.submit(create_inner_zip, i, number,  json_count)
            for i in range(submission_count)
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
        Key=transmission_zip_name,
        Body=outer_zip_buffer.getvalue(),
        ContentType="application/zip"
    )

    return {
        "message": f"{len(inner_zip_results)} inner ZIPs uploaded successfully",
        "s3_bucket": BUCKET_NAME,
        "s3_key": transmission_zip_name
    }
