"""Create concrete User storage backends from parameters (shared by server and storage_worker)."""

from common.io.storage import PickleStorage, Storage

from .io.storage import MongoUserStorage, PostgresUserStorage, Sqlite3UserStorage
from .user import User

__all__ = ["create_user_storage_backend"]


def _postgres_conninfo(
  host: str,
  port: int,
  db: str,
  user: str,
  password: str,
) -> str:
  return f"host={host} port={port} dbname={db} user={user} password={password}"


def _mongodb_user_and_password(user: str, password: str) -> tuple[str | None, str | None]:
  u = user.strip() or None
  p = password if u else None
  return u, p


def create_user_storage_backend(
  storage_type: str,
  *,
  pickle_storage_dirname: str = "db.pickle",
  sqlite3_storage_filename: str = "db.sqlite3",
  postgres_host: str = "localhost",
  postgres_port: int = 5432,
  postgres_db: str = "admin_panel",
  postgres_user: str = "admin",
  postgres_password: str = "admin",
  mongodb_host: str = "localhost",
  mongodb_port: int = 27017,
  mongodb_db: str = "admin_panel",
  mongodb_user: str = "",
  mongodb_password: str = "",
) -> Storage[User]:
  match storage_type:
    case "pickle":
      return PickleStorage(pickle_storage_dirname)
    case "sqlite3":
      return Sqlite3UserStorage(sqlite3_storage_filename)
    case "postgres":
      return PostgresUserStorage(
        _postgres_conninfo(
          postgres_host,
          postgres_port,
          postgres_db,
          postgres_user,
          postgres_password,
        )
      )
    case "mongodb":
      mu, mp = _mongodb_user_and_password(mongodb_user, mongodb_password)
      return MongoUserStorage(
        host=mongodb_host,
        port=mongodb_port,
        database=mongodb_db,
        user=mu,
        password=mp,
      )
    case _:
      raise ValueError(f"Unknown storage type: {storage_type}")
