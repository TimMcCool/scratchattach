"""
Scratchattach CLI. Most source code is in the `cli` directory
"""

import argparse

from scratchattach import cli
from scratchattach.cli import db, cmd

import rich.traceback

rich.traceback.install()


# noinspection PyUnusedLocal
def main():
    parser = argparse.ArgumentParser(
        prog="scratch",
        description="Scratchattach CLI",
        epilog=f"Running scratchattach CLI version {cli.VERSION}",
    )

    # Using walrus operator & ifs for artificial indentation
    if commands := parser.add_subparsers(dest="command"):
        if login := commands.add_parser("login", help="Login to Scratch"):
            login.add_argument("--sessid", dest="sessid", nargs="?", default=False, const=True,
                               help="Login by session ID")
        if group := commands.add_parser("group", help="View current session group"):
            if group_commands := group.add_subparsers(dest="group_command"):
                if group_list := group_commands.add_parser("list", help="List all session groups"):
                    ...

    args = parser.parse_args(namespace=cli.ArgSpace())
    cli.ctx.args = args
    cli.ctx.parser = parser

    match args.command:
        case "login":
            cmd.login()
        case "group":
            cmd.group()
        case None:
            parser.print_help()


if __name__ == '__main__':
    main()
