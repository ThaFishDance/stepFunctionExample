import csv
import os
from uuid import uuid4
from io import StringIO

import boto3


def get_doc_codes(domain: str) -> list:
    # TODO: hard coding for now
    return ["dc1", "dc2", "dc3"]


def create_transmissions(domain: str, number_of_transmissions: int, job_id: uuid4) -> int:
    # Define document codes (fixed for now)
    doc_codes = get_doc_codes(domain)
    all_transmission_names = []

    # Create list of transmission names
    for doc_code in doc_codes:
        for i in range(number_of_transmissions):
            transmission_name = f"{domain}_{doc_code}_{i}"
            all_transmission_names.append(transmission_name)

    # Create CSV in memory
    csv_buffer = StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(["TransmissionName"])  # Header
    for name in all_transmission_names:
        writer.writerow([name])

    # Upload to S3
    s3 = boto3.client("s3")
    bucket_name = os.environ.get("BUCKET_NAME")
    key = f"{job_id}.csv"
    s3.put_object(Bucket=bucket_name, Key=key, Body=csv_buffer.getvalue())

    return len(all_transmission_names)


def lambda_handler(event, context):
    print(event)
    print(context)

    # Given a domain
    # Number of transmissions per doc_code
    domain = "CI"  # TODO hardcoding for now
    number_of_transmissions = 1  # TODO hardcoding for now
    job_id = uuid4()

    total_transmissions = create_transmissions(domain, number_of_transmissions, job_id)

    return {
        "job_id": job_id,
        "numbers": list(range(total_transmissions))
    }
