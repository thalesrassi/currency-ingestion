import io
import os

import boto3
import pyarrow.parquet as pq
from dotenv import load_dotenv

load_dotenv()

bucket_url = os.environ["MINIO_BUCKET_URL"]
aws_access_key_id = os.environ["MINIO_ROOT_USER"]
aws_secret_access_key = os.environ["MINIO_ROOT_PASSWORD"]
endpoint_url = os.environ["MINIO_ENDPOINT_URL"]

s3 = boto3.client(
    "s3",
    endpoint_url=endpoint_url,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
)

bucket = bucket_url.removeprefix("s3://")

prefix = "latest/latest_rates/"

paginator = s3.get_paginator("list_objects_v2")
pages = paginator.paginate(Bucket=bucket, Prefix=prefix)

parquet_keys = [
    obj["Key"]
    for page in pages
    for obj in page.get("Contents", [])
    if obj["Key"].endswith(".parquet")
]

if not parquet_keys:
    print(f"Nenhum arquivo Parquet encontrado em: s3://{bucket}/{prefix}")
else:
    print(f"Encontrados {len(parquet_keys)} arquivo(s):\n")
    for key in parquet_keys:
        print(f"  s3://{bucket}/{key}")
    print("\n============================//===============================\n")

for parquet_path in parquet_keys:
    print(f"\nArquivo {parquet_path.removeprefix(prefix)}: \n")
    response = s3.get_object(Bucket=bucket, Key=parquet_path)
    buffer = io.BytesIO(response["Body"].read())
    table = pq.read_table(buffer)
    print(table.to_pandas())