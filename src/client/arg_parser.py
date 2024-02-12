from argparse import ArgumentParser

from .config  import Config


__all__ = ["arg_parser"]


arg_parser = ArgumentParser(
    prog        = "client",
    description = "Terminal-based REST client for admin-panel's server",
    epilog      = "This is just a self-educational project",
)

arg_parser.add_argument(
    "-a",
    "--address",
    
    default = Config.address,
    metavar = "<address>",
    help    = f"server's REST API address (default value is {repr(Config.address)})",
)
