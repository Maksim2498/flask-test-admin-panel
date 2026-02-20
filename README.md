# Admin Panel

## Table of Contents

- [Table of Contents](#table-of-contents);
- [About](#about);
- [Requirements](#requirements);
- [Running](#running);
- [Development](#development);
  - [Server](#server);
  - [Client](#client).

## About

This is a self-educational project created only for sake
of trying to build a simple CRUD project using the
[Flask framework](https://flask.palletsprojects.com/en/3.0.x/).

It consists of the two parts:

- [Server](./src/server/);
- [Client](./src/client/).

Server runs a RESTful API and SSR web-app.

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

| Option                       | Allowed Arguments         | Default Value  | Description                                                 |
|------------------------------|---------------------------|----------------|-------------------------------------------------------------|
| `-h`, `--help`               | -                         | -              | show help                                                   |
| `--web-url-prefix`           | `str`                     | `"/"`          | URL prefix of the web-app                                   |
| `--api-url-prefix`           | `str`                     | `"/api"`       | URL prefix of the REST API                                  |
| `--secret-filename`          | `str`                     | `"secret.key"` | filename of the secret key                                  |
| `--secret-len`               | `int` in range [1, 2^16)  | `64`           | length of the secret key                                    |
| `-p`, `--port`               | `int` in range [0, 2^16)  | `8000`         | port number                                                 |
| `-s`, `--storage-type`       | `"pickle"` or `"sqlite3"` | `"pickle"`     | type of the storage to be used                              |
| `--pickle-storage-dirname`   | `str`                     | `"db.pickle"`  | name of the directory pickle storage uses to store database |
| `--sqlite3-storage-filename` | `str`                     | `"db.sqlite3"` | filename of the Sqlite3 database                            |
| `-d`, `--debug`              | -                         | -              | enables debug mode                                          |

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
