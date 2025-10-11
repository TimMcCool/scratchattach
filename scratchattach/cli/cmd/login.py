from scratchattach.cli.context import ctx, console
from scratchattach.cli import db
from rich.markup import escape

from getpass import getpass

import scratchattach as sa
import warnings

warnings.filterwarnings("ignore", category=sa.LoginDataWarning)


def login():
    if ctx.args.sessid:
        if isinstance(ctx.args.sessid, bool):
            ctx.args.sessid = getpass("Session ID: ")

        session = sa.login_by_id(ctx.args.sessid)
        password = None
    else:
        username = input("Username: ")
        password = getpass()

        session = sa.login(username, password)

    console.rule()
    console.print(f"Logged in as [b]{session.username}[/]")

    # register session
    db.conn.execute("BEGIN")
    db.cursor.execute(
        "INSERT OR REPLACE INTO SESSIONS (ID, USERNAME, PASSWORD) "
        "VALUES (?, ?, ?)", (session.id, session.username, password)
    )
    db.conn.commit()

    # make new group
    db.cursor.execute("SELECT NAME FROM GROUPS WHERE NAME = ?", (session.username,))
    if not db.cursor.fetchone():
        console.rule(f"Registering [b]{escape(session.username)}[/] as group")
        db.conn.execute("BEGIN")
        db.cursor.execute(
            "INSERT INTO GROUPS (NAME, DESCRIPTION) "
            "VALUES (?, ?)", (session.username, input(f"Description for {session.username}: "))
        ).execute(
            "INSERT INTO GROUP_USERS (GROUP_NAME, USERNAME) "
            "VALUES (?, ?)", (session.username, session.username)
        )

        db.conn.commit()

    console.rule()
    if input("Add to current session group? (Y/n)").lower() not in ("y", ''):
        return

    db.conn.execute("BEGIN")
    db.cursor.execute("INSERT INTO GROUP_USERS (GROUP_NAME, USERNAME) "
                      "VALUES (?, ?)", (ctx.current_group_name, session.username))
    db.conn.commit()
    console.print(f"Added to [b]{escape(ctx.current_group_name)}[/]")
