import os
import dlt
from dlt.destinations import filesystem
from ingestion.source import freecurrency_source

def build_pipeline(bucket_url,aws_access_key_id,aws_secret_access_key,endpoint_url):
    destination = filesystem(
        bucket_url = bucket_url,
        credentials = {
            "aws_access_key_id" : aws_access_key_id,
            "aws_secret_access_key" : aws_secret_access_key,
            "endpoint_url" : endpoint_url
        }
    )

    pipeline_local = dlt.pipeline(
        pipeline_name = "freecurrency_pipeline",
        destination = destination,
        dataset_name = "latest",
    )

    return pipeline_local

def run_pipeline():

    api_key = os.environ["API_KEY"]
    bucket_url = os.environ["MINIO_BUCKET_URL"]
    aws_access_key_id = os.environ["AWS_ACCESS_KEY_ID"]
    aws_secret_access_key = os.environ["AWS_SECRET_ACCESS_KEY"]
    endpoint_url = os.environ["MINIO_ENDPOINT_URL"]

    pipeline_local = build_pipeline(bucket_url,aws_access_key_id,aws_secret_access_key,endpoint_url)

    load_info = pipeline_local.run(freecurrency_source(api_key=api_key), loader_file_format="parquet")
    
    return load_info.loads_ids[0]

    