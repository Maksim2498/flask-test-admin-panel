from random            import randint
from typing            import Sequence

from flask             import Flask

from common.io.storage import Storage
from common.user       import UserManager, User

from .blueprint.api    import create_blueprint as creaet_api_blueprint
from .blueprint.web    import create_blueprint as create_web_blueprint
from .io.storage       import PickleStorage
from .user.io.storage  import Sqlite3UserStorage
from .arg_parser       import arg_parser
from .config           import Config

import sys


def create_config(args: Sequence[str] = sys.argv[1:]) -> Config:
    parsed_args = arg_parser.parse_args(args)
    config      = Config(**parsed_args.__dict__)

    return config

def create_user_manager(config: Config) -> UserManager:
    return UserManager(create_storage(config))

def create_storage(config: Config) -> Storage[User]:
    match config.storage_type:
        case "pickle":
            return PickleStorage(config.pickle_storage_dirname)

        case "sqlite3":
            return Sqlite3UserStorage(config.sqlite3_storage_filename)

def create_app(config: Config, user_manager: UserManager) -> Flask:
    app = Flask(__name__)

    app.register_blueprint(creaet_api_blueprint(user_manager), url_prefix = config.api_url_prefix)
    app.register_blueprint(create_web_blueprint(user_manager), url_prefix = config.web_url_prefix)

    app.secret_key = read_or_create_secret_key_if_not_exists(config)

    return app

def read_or_create_secret_key_if_not_exists(config: Config) -> str:
    try:
        return read_secret_key(config)
    except FileNotFoundError:
        return create_secret_key(config)

def read_secret_key(config: Config) -> str:
    with open(config.secret_filename, "r") as file:
        return file.read()

def create_secret_key(config: Config) -> str:
    key = "".join([str(randint(0, 9)) for _ in range(config.secret_len)])

    with open(config.secret_filename, "w") as file:
        file.write(key)

    return key


config       = create_config()
user_manager = create_user_manager(config)
app          = create_app(config, user_manager)

app.run(
    port  = config.port,
    debug = config.debug,
)
