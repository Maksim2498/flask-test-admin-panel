import sys
from collections.abc import Sequence
from random import randint

from flask import Flask

from common.io.storage import Storage
from common.user import User, UserManager
from common.user.io.storage import RabbitmqUserStorage
from common.user.storage_factory import create_user_storage_backend

from .arg_parser import arg_parser
from .blueprint.api import create_blueprint as create_api_blueprint
from .blueprint.web import create_blueprint as create_web_blueprint
from .config import Config
from .multi_user_manager import MultiUserManager


def create_config(args: Sequence[str] = sys.argv[1:]) -> Config:
  parsed_args = arg_parser.parse_args(args)
  args_dict = dict(parsed_args.__dict__)
  enabled_str = args_dict.pop("enabled_storages", "pickle,sqlite3")
  args_dict["enabled_storages"] = [s.strip() for s in str(enabled_str).split(",") if s.strip()]

  config = Config(**args_dict)
  return config


def create_storage(config: Config, storage_type: str) -> Storage[User]:
  if storage_type == "rabbitmq":
    return RabbitmqUserStorage(
      config.rabbitmq_url,
      queue=config.rabbitmq_rpc_queue,
      timeout=config.rabbitmq_rpc_timeout,
    )
  return create_user_storage_backend(
    storage_type,
    pickle_storage_dirname=config.pickle_storage_dirname,
    sqlite3_storage_filename=config.sqlite3_storage_filename,
    postgres_host=config.postgres_host,
    postgres_port=config.postgres_port,
    postgres_db=config.postgres_db,
    postgres_user=config.postgres_user,
    postgres_password=config.postgres_password,
    mongodb_host=config.mongodb_host,
    mongodb_port=config.mongodb_port,
    mongodb_db=config.mongodb_db,
    mongodb_user=config.mongodb_user,
    mongodb_password=config.mongodb_password,
  )


def create_multi_user_manager(config: Config) -> MultiUserManager:
  managers: dict[str, UserManager] = {}
  for name in config.enabled_storages:
    storage = create_storage(config, name)
    managers[name] = UserManager(storage)
  return MultiUserManager(managers, config.enabled_storages)


def create_app(config: Config, multi_manager: MultiUserManager) -> Flask:
  app = Flask(__name__)

  app.register_blueprint(create_api_blueprint(multi_manager), url_prefix=config.api_url_prefix)
  app.register_blueprint(create_web_blueprint(multi_manager), url_prefix=config.web_url_prefix)

  app.secret_key = read_or_create_secret_key_if_not_exists(config)

  return app


def read_or_create_secret_key_if_not_exists(config: Config) -> str:
  try:
    return read_secret_key(config)
  except FileNotFoundError:
    return create_secret_key(config)


def read_secret_key(config: Config) -> str:
  with open(config.secret_filename) as file:
    return file.read()


def create_secret_key(config: Config) -> str:
  key = "".join([str(randint(0, 9)) for _ in range(config.secret_len)])

  with open(config.secret_filename, "w") as file:
    file.write(key)

  return key


config = create_config()
multi_manager = create_multi_user_manager(config)
app = create_app(config, multi_manager)

if __name__ == "__main__":
  app.run(
    host=config.host,
    port=config.port,
    debug=config.debug,
  )
