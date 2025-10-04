from scratchattach.cli.context import ctx
from scratchattach.cli import db

from getpass import getpass

import scratchattach as sa
import warnings

warnings.filterwarnings("ignore", category=sa.LoginDataWarning)

def login_by_sessid():
    raise NotImplementedError

def login():
    print(ctx.args)

    if ctx.args.sessid:
        login_by_sessid()
        return

    username = input("Username: ")
    password = getpass()

    session = sa.login(username, password)
    db.conn.execute("BEGIN")
    db.cursor.execute(
        "INSERT OR REPLACE INTO SESSIONS (ID, USERNAME, PASSWORD) "
        "VALUES (?, ?, ?)", (session.id, session.username, password)
    )
    db.conn.commit()
