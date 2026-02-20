from dataclasses import dataclass
from typing import Literal, TypeAlias

__all__ = [
  "Config",
  "StorageType",
]


StorageType: TypeAlias = Literal["pickle", "sqlite3"]


@dataclass
class Config:
  web_url_prefix: str = "/"
  api_url_prefix: str = "/api"
  secret_filename: str = "secret.key"
  secret_len: int = 64
  port: int = 8000
  host: str = "127.0.0.1"
  storage_type: StorageType = "pickle"
  pickle_storage_dirname: str = "db.pickle"
  sqlite3_storage_filename: str = "db.sqlite3"
  debug: bool = False
