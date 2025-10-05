"""
Handles data like current session for 'sessionable' commands.
Holds objects that should be available for the whole CLI system
Also provides wrappers for some SQL info.
"""
import argparse
from dataclasses import dataclass, field

import rich.console
from typing_extensions import Optional

from scratchattach.cli.namespace import ArgSpace
from scratchattach.cli import db
import scratchattach as sa


@dataclass
class _Ctx:
    args: ArgSpace = field(default_factory=ArgSpace)
    parser: argparse.ArgumentParser = field(default_factory=argparse.ArgumentParser)
    sessions: list[sa.Session] = field(default_factory=list)
    _session: Optional[sa.Session] = None

    # TODO: implement this
    def sessionable(self, func):
        """
        Decorate a command that will be run for every session in the group.
        """

        def wrapper(*args, **kwargs):
            for session in self.sessions:
                self._session = session
                func(*args, **kwargs)

        return wrapper

    @property
    def session(self):
        return self._session

    # helper functions with DB
    # if possible, put all db funcs here

    @property
    def current_group_name(self):
        return db.cursor \
            .execute("SELECT * FROM CURRENT WHERE GROUP_NAME IS NOT NULL") \
            .fetchone()[0]

    @staticmethod
    def db_group_exists(name: str) -> bool:
        return db.cursor.execute("SELECT NAME FROM GROUPS WHERE NAME = ?", (name,)).fetchone() is not None

    @staticmethod
    def db_session_exists(name: str) -> bool:
        return db.cursor.execute("SELECT USERNAME FROM SESSIONS WHERE USERNAME = ?", (name,)).fetchone() is not None

    @staticmethod
    def db_users_in_group(name: str) -> list[str]:
        return [i for (i,) in db.cursor.execute(
            "SELECT USERNAME FROM GROUP_USERS WHERE GROUP_NAME = ?", (name,)).fetchall()]

    def db_add_to_group(self, group_name: str, username: str):
        if username in self.db_users_in_group(group_name) or not self.db_session_exists(username):
            return
        db.conn.execute("BEGIN")
        db.cursor.execute("INSERT INTO GROUP_USERS (GROUP_NAME, USERNAME) "
                          "VALUES (?, ?)", (group_name, username))
        db.conn.commit()

ctx = _Ctx()
console = rich.console.Console()


def format_esc(text: str, *args, **kwargs) -> str:
    """
    Format string with args, escaped.
    """

    def esc(s):
        return rich.console.escape(s) if isinstance(s, str) else s

    kwargs = {k: esc(v) for k, v in kwargs.items()}
    return text.format(*map(esc, args), **kwargs)
