from scratchattach.cli.context import ctx
from scratchattach.cli import db

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

    db.conn.execute("BEGIN")
    db.cursor.execute(
        "INSERT OR REPLACE INTO SESSIONS (ID, USERNAME) "
        "VALUES (?, ?)", (session.id, session.username)
    )
    db.conn.commit()
