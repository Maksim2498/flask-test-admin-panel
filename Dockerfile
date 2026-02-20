FROM tiangolo/uwsgi-nginx:python3.12

ENV LISTEN_PORT 8000
EXPOSE 8000

WORKDIR /app

COPY pyproject.toml .
COPY src ./src
COPY uwsgi.ini .
RUN pip install --no-cache-dir -e .
