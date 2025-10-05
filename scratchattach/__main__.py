"""
Scratchattach CLI. Most source code is in the `cli` directory
"""

import argparse

from scratchattach import cli
from scratchattach.cli import db, cmd
from scratchattach.cli.context import ctx, console

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
        commands.add_parser("profile", help="View your profile")
        if login := commands.add_parser("login", help="Login to Scratch"):
            login.add_argument("--sessid", dest="sessid", nargs="?", default=False, const=True,
                               help="Login by session ID")
        if group := commands.add_parser("group", help="View current session group"):
            if group_commands := group.add_subparsers(dest="group_command"):
                group_commands.add_parser("list", help="List all session groups")
                group_commands.add_parser("add", help="Add sessions to group")
                group_commands.add_parser("remove", help="Remove sessions from a group")
                if group_new := group_commands.add_parser("new", help="Create a new group"):
                    group_new.add_argument("group_name")
                if group_switch := group_commands.add_parser("switch", help="Change the current group"):
                    group_switch.add_argument("group_name")

    parser.add_argument("-U", "--username", dest="username", help="Name of user to look at")
    parser.add_argument("-P", "--project", dest="project_id", help="ID of project to look at")
    parser.add_argument("-S", "--studio", dest="studio_id", help="ID of studio to look at")

    args = parser.parse_args(namespace=cli.ArgSpace())
    cli.ctx.args = args
    cli.ctx.parser = parser

    match args.command:
        case "login":
            cmd.login()
        case "group":
            cmd.group()
        case "profile":
            cmd.profile()
        case None:
            if args.username:
                user = ctx.session.connect_user(args.username)
                console.print(cli.try_get_img(user.icon, (30, 30)))
                console.print(user)
                return
            if args.studio_id:
                console.print(ctx.session.connect_studio(args.studio_id))
                return
            if args.project_id:
                console.print(ctx.session.connect_project(args.project_id))
                return

            parser.print_help()


if __name__ == '__main__':
    main()
