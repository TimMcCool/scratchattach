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
        commands.add_parser("sessions", help="View session list")
        if login := commands.add_parser("login", help="Login to Scratch"):
            login.add_argument("--sessid", dest="sessid", nargs="?", default=False, const=True,
                               help="Login by session ID")
        if group := commands.add_parser("group", help="View current session group"):
            if group_commands := group.add_subparsers(dest="group_command"):
                group_commands.add_parser("list", help="List all session groups")
                group_commands.add_parser("add", help="Add sessions to group")
                group_commands.add_parser("remove", help="Remove sessions from a group")
                group_commands.add_parser("delete", help="Delete current group")
                if group_copy := group_commands.add_parser("copy", help="Copy current group with a new name"):
                    group_copy.add_argument("group_name", help="New group name")
                if group_rename := group_commands.add_parser("rename", help="Rename current group"):
                    group_rename.add_argument("group_name", help="New group name")
                if group_new := group_commands.add_parser("new", help="Create a new group"):
                    group_new.add_argument("group_name")
                if group_switch := group_commands.add_parser("switch", help="Change the current group"):
                    group_switch.add_argument("group_name")

    parser.add_argument("-U", "--username", dest="username", help="Name of user to look at")
    parser.add_argument("-P", "--project", dest="project_id", help="ID of project to look at")
    parser.add_argument("-S", "--studio", dest="studio_id", help="ID of studio to look at")
    parser.add_argument("-L", "--session_name", dest="session_name",
                        help="Name of (registered) session/login to look at")

    args = parser.parse_args(namespace=cli.ArgSpace())
    cli.ctx.args = args
    cli.ctx.parser = parser

    match args.command:
        case "sessions":
            cmd.sessions()
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
                studio = ctx.session.connect_studio(args.studio_id)
                console.print(cli.try_get_img(studio.thumbnail, (34, 20)))
                console.print(studio)
                return
            if args.project_id:
                project = ctx.session.connect_project(args.project_id)
                console.print(cli.try_get_img(project.thumbnail, (30, 23)))
                console.print(project)
                return
            if args.session_name:
                if sess := ctx.db_get_sess(args.session_name):
                    console.print(sess)
                else:
                    raise ValueError(f"No session logged in called {args.session_name!r} "
                                     f"- try using `scratch sessions` to see available sessions")
                return

            parser.print_help()


if __name__ == '__main__':
    main()
