import sys
from collections.abc import Sequence

from .arg_parser import arg_parser
from .config import Config
from .io.dialog import CliDialog
from .menu import Menu
from .user.io.storage import RestUserStorage


def create_config(args: Sequence[str] = sys.argv[1:]) -> Config:
  parsed_args = arg_parser.parse_args(args)
  config = Config(**parsed_args.__dict__)

  return config


config = create_config()
dialog = CliDialog()
storage = RestUserStorage(config.address)
menu = Menu(dialog, storage)

menu.run()
