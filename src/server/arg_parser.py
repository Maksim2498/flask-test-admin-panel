from argparse import ArgumentError, ArgumentParser
from gettext import gettext
from typing import override

from .config import Config

__all__ = ["arg_parser"]


class ServerArgumentParser(ArgumentParser):
  # Overriding private method is
  # quite a bad practice, i know,
  # but it isn't a real project
  # so...

  @override
  def _check_value(self, action, value):
    if action.choices is not None and value not in action.choices:
      if isinstance(action.choices, range):
        choices_str = f"[{action.choices.start}-{action.choices.stop})"
      else:
        choices_str = ", ".join(map(repr, action.choices))

      args = {
        "value": value,
        "choices": choices_str,
      }

      msg = gettext("invalid choice: %(value)r (choose from %(choices)s)")

      raise ArgumentError(action, msg % args)


arg_parser = ServerArgumentParser(
  prog="server",
  description="SSR and REST API web server for admin panel web-app",
  epilog="This is just a self-educational project",
)

arg_parser.add_argument(
  "--web-url-prefix",
  default=Config.web_url_prefix,
  metavar="<url prefix>",
  help="URL prefix of the web-app (default value is {repr(Config.web_url_prefix)})",
)

arg_parser.add_argument(
  "--api-url-prefix",
  default=Config.api_url_prefix,
  metavar="<url prefix>",
  help=f"URL prefix of the REST API (default value is {repr(Config.api_url_prefix)})",
)

arg_parser.add_argument(
  "--secret-filename",
  default=Config.secret_filename,
  metavar="<filename>",
  help=f"filename of the secret key (default value is {repr(Config.secret_filename)})",
)

arg_parser.add_argument(
  "--secret-len",
  default=Config.secret_len,
  type=int,
  choices=range(1, 2**16),
  metavar=f"[1-{2**16})",
  help=f"length of the secret key (default value is {Config.secret_len})",
)

arg_parser.add_argument(
  "-p",
  "--port",
  default=Config.port,
  type=int,
  choices=range(0, 2**16),
  help=f"port number (default value is {Config.port})",
  metavar=f"[0-{2**16})",
)

arg_parser.add_argument(
  "--host",
  default=Config.host,
  metavar="<host>",
  help=f"host to bind to (default value is {repr(Config.host)})",
)

arg_parser.add_argument(
  "--enabled-storages",
  default="pickle,sqlite3",
  metavar="<pickle,sqlite3>",
  help="comma-separated list of enabled storage backends (default: pickle,sqlite3)",
)

arg_parser.add_argument(
  "--pickle-storage-dirname",
  default=Config.pickle_storage_dirname,
  metavar="<dirname>",
  help=f"name of the directory pickle storage uses to store database (default value is {repr(Config.pickle_storage_dirname)})",
)

arg_parser.add_argument(
  "--sqlite3-storage-filename",
  default=Config.sqlite3_storage_filename,
  metavar="<filename>",
  help=f"filename of the Sqlite3 database (default value is {repr(Config.sqlite3_storage_filename)})",
)

arg_parser.add_argument(
  "-d",
  "--debug",
  default=Config.debug,
  action="store_true",
  help="enable debug mode",
)
