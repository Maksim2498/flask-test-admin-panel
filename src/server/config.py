from dataclasses import dataclass, field
from typing import Literal, TypeAlias

__all__ = [
  "Config",
  "StorageType",
]


StorageType: TypeAlias = Literal["pickle", "sqlite3", "postgres", "mongodb", "rabbitmq"]


@dataclass
class Config:
  web_url_prefix: str = "/"
  api_url_prefix: str = "/api"
  secret_filename: str = "secret.key"
  secret_len: int = 64
  port: int = 8000
  host: str = "127.0.0.1"
  enabled_storages: list[str] = field(default_factory=lambda: ["pickle", "sqlite3"])
  pickle_storage_dirname: str = "db.pickle"
  sqlite3_storage_filename: str = "db.sqlite3"
  postgres_host: str = "localhost"
  postgres_port: int = 5432
  postgres_db: str = "admin_panel"
  postgres_user: str = "admin"
  postgres_password: str = "admin"
  mongodb_host: str = "localhost"
  mongodb_port: int = 27017
  mongodb_db: str = "admin_panel"
  mongodb_user: str = ""
  mongodb_password: str = ""
  rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
  rabbitmq_rpc_queue: str = "admin_panel.user.storage.rpc"
  rabbitmq_rpc_timeout: float = 30.0
  debug: bool = False
