FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY src ./src
RUN pip install --no-cache-dir -e .

WORKDIR /app/src

EXPOSE 8000

CMD ["python", "-m", "server", "--host", "0.0.0.0", "--secret-filename", "/app/data/secret.key", "--sqlite3-storage-filename", "/app/data/db.sqlite3", "--storage-type", "sqlite3", "-p", "8000"]
