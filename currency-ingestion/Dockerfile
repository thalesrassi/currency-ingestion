FROM python:3.10-slim
WORKDIR /app

COPY pyproject.toml .
COPY script_02.py .
COPY uv.lock .

RUN pip install uv
RUN uv sync

CMD ["uv", "run", "python", "script_02.py"]