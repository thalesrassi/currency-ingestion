FROM apache/airflow:2.9.1-python3.11

COPY --from=ghcr.io/astral-sh/uv:0.9.0 /uv /home/airflow/.local/bin/uv

COPY pyproject.toml uv.lock /opt/airflow/

WORKDIR /opt/airflow
RUN uv export --frozen --no-dev --no-emit-project -o /tmp/requirements.txt && \
    pip install --no-cache-dir -r /tmp/requirements.txt && \
    pip install --no-cache-dir "pydantic>=2.8.0,<3.0.0"