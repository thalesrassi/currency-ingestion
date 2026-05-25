import dlt
import requests
from datetime import datetime, timezone
from typing import Iterator
from dlt.sources import DltResource

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
