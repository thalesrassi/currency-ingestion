import os
import dlt
import requests
from datetime import datetime, timezone
from typing import Iterator
from dotenv import load_dotenv
from dlt.sources import DltResource
from dlt.destinations import filesystem

BASE_URL = "https://api.freecurrencyapi.com/v1"
DEFAULT_CURRENCIES = "USD,EUR,GBP,JPY"

@dlt.resource(name="latest_rates",write_disposition="append")
def latest_rates(api_key: str, base_currency: str, currencies: str) -> Iterator[dict]:
    response = requests.get( 
        f"{BASE_URL}/latest",
        params={
            "apikey": api_key,
            "base_currency": base_currency,
            "currencies": currencies
        },
        timeout=30,
    )
    response.raise_for_status()

    data = response.json().get("data", {})
    extracted_at = datetime.now(timezone.utc).isoformat()


    for target_currency, rate in data.items():
        yield {
            "base_currency": base_currency,
            "target_currency": target_currency,
            "rate": rate,
            "extracted_at": extracted_at,
        }

@dlt.source(name="freecurrency")
def freecurrency_source(
    api_key: str,
    base_currency: str = "BRL",
    currencies: str = DEFAULT_CURRENCIES,
) -> DltResource:
    return latest_rates(api_key=api_key, base_currency=base_currency, currencies=currencies)

if __name__ == "__main__":
    load_dotenv()
    
    api_key = os.environ["API_KEY"]
    bucket_url = os.environ["MINIO_BUCKET_URL"]
    aws_access_key_id = os.environ["AWS_ACCESS_KEY_ID"]
    aws_secret_access_key = os.environ["AWS_SECRET_ACCESS_KEY"]
    endpoint_url = os.environ["MINIO_ENDPOINT_URL"]

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

    load_info = pipeline_local.run(freecurrency_source(api_key=api_key))
    print(load_info)