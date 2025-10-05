from scratchattach.cli.context import ctx, console
from scratchattach.cli import db
from rich.console import escape

from getpass import getpass

import scratchattach as sa
import warnings

warnings.filterwarnings("ignore", category=sa.LoginDataWarning)


def login():
    if ctx.args.sessid:
        if isinstance(ctx.args.sessid, bool):
            ctx.args.sessid = getpass("Session ID: ")

        session = sa.login_by_id(ctx.args.sessid)
    else:
        username = input("Username: ")
        password = getpass()

        session = sa.login(username, password)

    # register session
    db.conn.execute("BEGIN")
    db.cursor.execute(
        "INSERT OR REPLACE INTO SESSIONS (ID, USERNAME) "
        "VALUES (?, ?)", (session.id, session.username)
    )
    db.conn.commit()

    # make new group
    db.cursor.execute("SELECT NAME FROM GROUPS WHERE NAME = ?", (session.username,))
    if not db.cursor.fetchone():
        console.print(f"Registering [blue]{escape(session.username)}[/] as group")
        db.conn.execute("BEGIN")
        db.cursor.execute(
            "INSERT INTO GROUPS (NAME, DESCRIPTION) "
            "VALUES (?, ?)", (session.username, input(f"Description for {session.username}: "))
        ).execute(
            "INSERT INTO GROUP_USERS (GROUP_NAME, USERNAME) "
            "VALUES (?, ?)", (session.username, session.username)
        )

        db.conn.commit()
