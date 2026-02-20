# Admin Panel

## Table of Contents

- [Table of Contents](#table-of-contents);
- [About](#about);
- [Requirements](#requirements);
- [Running](#running);
- [Development](#development);
- [Docker](#docker).

## About

This is a self-educational project created only for sake
of trying to build a simple CRUD project using the
[Flask framework](https://flask.palletsprojects.com/en/3.0.x/).

It consists of the two parts:

- [Server](./src/server/);
- [Client](./src/client/).

Server runs a RESTful API and SSR web-app. Multiple storage backends (pickle, sqlite3, postgres, mongodb, **rabbitmq**) can be enabled at once; each request selects one via the `storage` query parameter (API) or radio switcher (web UI). The **rabbitmq** backend talks to a separate **storage worker** process over RabbitMQ (JSON RPC); the worker uses one of the local backends internally (pickle by default in Compose).

Client, in turn, provides a simple terminal-based access
to the RESTful API provided by the server.

## Requirements

- [Python 3.12](https://www.python.org/downloads/);
- [Flask 3.0.x](https://flask.palletsprojects.com/en/3.0.x/) (for server);
- [Requests 2.x.x](https://pypi.org/project/requests/) (for client).

Exact versions used in development are specified in the [pyproject.toml](./pyproject.toml).

## Running

To run server or client you must firstly set your working directory to the [src](./src/).
When you are ready, proceed to the following sections.

### Server

To run server with the default options simply execute the following command in your terminal:

```bash
python3 -m server
```

You can additionally pass a one or more arguments to the server. The following table contains
a list of available options with their default values and description.

| Option                       | Allowed Arguments         | Default Value      | Description                                                 |
|------------------------------|---------------------------|--------------------|-------------------------------------------------------------|
| `-h`, `--help`               | -                         | -                  | show help                                                   |
| `--web-url-prefix`           | `str`                     | `"/"`              | URL prefix of the web-app                                   |
| `--api-url-prefix`           | `str`                     | `"/api"`           | URL prefix of the REST API                                  |
| `--secret-filename`          | `str`                     | `"secret.key"`     | filename of the secret key                                  |
| `--secret-len`               | `int` in range [1, 2^16)  | `64`               | length of the secret key                                    |
| `-p`, `--port`               | `int` in range [0, 2^16)  | `8000`             | port number                                                 |
| `--host`                     | `str`                     | `"127.0.0.1"`      | host to bind to                                             |
| `--enabled-storages`         | `str`                     | `"pickle,sqlite3"` | comma-separated: pickle, sqlite3, postgres, mongodb, rabbitmq |
| `--pickle-storage-dirname`   | `str`                     | `"db.pickle"`      | directory for pickle storage                                |
| `--sqlite3-storage-filename` | `str`                     | `"db.sqlite3"`     | filename for SQLite3 database                               |
| `--postgres-host`            | `str`                     | `"localhost"`      | PostgreSQL host                                             |
| `--postgres-port`            | `int`                     | `5432`             | PostgreSQL port                                             |
| `--postgres-db`              | `str`                     | `"admin_panel"`    | PostgreSQL database                                         |
| `--postgres-user`            | `str`                     | `"admin"`          | PostgreSQL user                                             |
| `--postgres-password`        | `str`                     | `"admin"`          | PostgreSQL password                                         |
| `--mongodb-host`             | `str`                     | `"localhost"`      | MongoDB host                                                |
| `--mongodb-port`             | `int`                     | `27017`            | MongoDB port                                                |
| `--mongodb-db`               | `str`                     | `"admin_panel"`    | MongoDB database                                            |
| `--mongodb-user`             | `str`                     | `""`               | MongoDB user (optional)                                     |
| `--mongodb-password`         | `str`                     | `""`               | MongoDB password (optional)                                 |
| `--rabbitmq-url`             | `str`                     | `amqp://guest:guest@localhost:5672/` | AMQP URL for `rabbitmq` storage                    |
| `--rabbitmq-rpc-queue`       | `str`                     | `admin_panel.user.storage.rpc` | must match worker `--rpc-queue`                    |
| `--rabbitmq-rpc-timeout`    | `float`                   | `30`               | RPC timeout (seconds)                                       |
| `-d`, `--debug`              | -                         | -                  | enables debug mode                                          |

### Storage worker (RabbitMQ RPC)

Runs the backend used by the `rabbitmq` storage. From the repo root (with `pip install -e .`):

```bash
python -m storage_worker --help
# example:
python -m storage_worker --rabbitmq-url amqp://guest:guest@localhost:5672/ --internal-storage pickle --pickle-storage-dirname ./rpc_data
```

Same CLI entry point: `storage-worker` (console script).

### Client

To run client with the default options simply execute the following command in your terminal:

```bash
python3 -m client
```

You can additionally pass a one or more arguments to the client. The following table contains
a list of available options with their default values and description.

| Option            | Allowed Arguments | Default Value                 | Description               |
|-------------------|-------------------|-------------------------------|---------------------------|
| `-h`, `--help`    | -                 | -                             | show help                 |
| `-a`, `--address` | `str`             | `"http://localhost:8000/api"` | server's REST API address |

## Development

### Virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or: .venv\Scripts\activate  # Windows

pip install -e ".[dev]"    # install with dev tools (ruff)
# or: pip install -e .     # install without dev tools
```

### Linting and formatting

```bash
ruff check src/          # run linter
ruff format src/         # format code
ruff check src/ --fix    # auto-fix lint issues
```

## Docker

```bash
docker compose up -d     # build and run in background
docker compose down      # stop and remove
```

- **Volumes**: `admin_panel_data` (secrets, pickle, sqlite3, worker pickle dir `rpc_pickle`), `mongodb_data`, `postgres_data`, `rabbitmq_data`
- **Port** 8000 — web: <http://localhost:8000>, API: <http://localhost:8000/api>
- **RabbitMQ** 3.13 management — AMQP `5672`, UI <http://localhost:15672> (guest/guest)
- **`storage_worker`** — image `Dockerfile.worker`, consumes queue `admin_panel.user.storage.rpc`, internal backend pickle at `/app/data/rpc_pickle`
- **PostgreSQL** 17 Alpine — user: admin, password: admin, DB: admin_panel
- **MongoDB** 7 — no auth by default; add `mongodb` to `ENABLED_STORAGES` to use
