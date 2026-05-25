from __future__ import annotations

import logging
from datetime import datetime, timedelta

from airflow.decorators import dag, task

logger = logging.getLogger(__name__)

DEFAULT_ARGS = {
    "owner": "data-engineering",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "retry_exponential_backoff": False,
    "email_on_failure": False,
    "email_on_retry": False,
}


@dag(
    dag_id="freecurrency_hourly_ingestion",
    description="Ingestão horária das cotações FreeCurrency API → MinIO (Parquet).",
    schedule="0 * * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    default_args=DEFAULT_ARGS,
    tags=["ingestion", "currency", "dlt", "minio"],
)
def currency_ingestion_dag() -> None:
    @task(task_id="run_dlt_pipeline")
    def run_dlt_pipeline() -> str:

        from ingestion.pipeline import run_pipeline

        result = run_pipeline()
        logger.info("Pipeline finalizado: %s", result)
        return result

    run_dlt_pipeline()


currency_ingestion_dag()