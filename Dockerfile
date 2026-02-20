FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY src ./src
RUN pip install --no-cache-dir -e .

WORKDIR /app/src

EXPOSE 8000

ARG POSTGRES_HOST=postgres
ARG POSTGRES_PORT=5432
ARG POSTGRES_DB=admin_panel
ARG POSTGRES_USER=admin
ARG POSTGRES_PASSWORD=admin

ENV POSTGRES_HOST=$POSTGRES_HOST
ENV POSTGRES_PORT=$POSTGRES_PORT
ENV POSTGRES_DB=$POSTGRES_DB
ENV POSTGRES_USER=$POSTGRES_USER
ENV POSTGRES_PASSWORD=$POSTGRES_PASSWORD

CMD python -m server \
  --host 0.0.0.0 \
  --secret-filename /app/data/secret.key \
  --pickle-storage-dirname /app/data/db.pickle \
  --sqlite3-storage-filename /app/data/db.sqlite3 \
  --enabled-storages pickle,sqlite3,postgres \
  --postgres-host $POSTGRES_HOST \
  --postgres-port $POSTGRES_PORT \
  --postgres-db $POSTGRES_DB \
  --postgres-user $POSTGRES_USER \
  --postgres-password $POSTGRES_PASSWORD \
  -p 8000
