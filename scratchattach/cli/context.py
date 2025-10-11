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
    _username: Optional[str] = None
    _session: Optional[sa.Session] = None

    # TODO: implement this
    def sessionable(self, func):
        """
        Decorate a command that will be run for every session in the group.
        """

        def wrapper(*args, **kwargs):
            for username in self.db_users_in_group(self.current_group_name):
                self._username = username
                self._session = None
                func(*args, **kwargs)

        return wrapper

    @property
    def username(self):
        if not self._username:
            self._username = self.db_users_in_group(self.current_group_name)[0]

        return self._username

    @property
    def session(self):
        if not self._session:
            self._session = sa.login_by_id(self.db_get_sessid(self.username))

        return self._session

    # helper functions with DB
    # if possible, put all db funcs here

    @property
    def current_group_name(self):
        return db.cursor \
            .execute("SELECT * FROM CURRENT WHERE GROUP_NAME IS NOT NULL") \
            .fetchone()[0]

    @current_group_name.setter
    def current_group_name(self, value: str):
        db.conn.execute("BEGIN")
        db.cursor.execute("DELETE FROM CURRENT WHERE GROUP_NAME IS NOT NULL")
        db.cursor.execute("INSERT INTO CURRENT (GROUP_NAME) VALUES (?)", (value,))
        db.conn.commit()

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

    def db_remove_from_group(self, group_name: str, username: str):
        if username in self.db_users_in_group(group_name):
            db.conn.execute("BEGIN")
            db.cursor.execute("DELETE FROM GROUP_USERS "
                              "WHERE USERNAME = ? AND GROUP_NAME = ?", (username, group_name))
            db.conn.commit()

    @staticmethod
    def db_get_sessid(username: str) -> Optional[str]:
        ret = db.cursor.execute("SELECT ID FROM SESSIONS WHERE USERNAME = ?", (username,)).fetchone()
        if ret:
            ret = ret[0]
        return ret

    def db_add_to_group(self, group_name: str, username: str):
        if username in self.db_users_in_group(group_name) or not self.db_session_exists(username):
            return
        db.conn.execute("BEGIN")
        db.cursor.execute("INSERT INTO GROUP_USERS (GROUP_NAME, USERNAME) "
                          "VALUES (?, ?)", (group_name, username))
        db.conn.commit()

    @staticmethod
    def db_group_delete(group_name: str):
        db.conn.execute("BEGIN")
        # delete links to sessions first
        db.cursor.execute("DELETE FROM GROUP_USERS WHERE GROUP_NAME = ?", (group_name,))
        # delete group itself
        db.cursor.execute("DELETE FROM GROUPS WHERE NAME = ?", (group_name,))
        db.conn.commit()

    @staticmethod
    def db_group_copy(group_name: str, copy_name: str):
        db.conn.execute("BEGIN")
        # copy group metadata
        db.cursor.execute("INSERT INTO GROUPS (NAME, DESCRIPTION) "
                          "SELECT ?, DESCRIPTION FROM GROUPS WHERE NAME = ?", (copy_name, group_name,))
        # copy sessions
        db.cursor.execute("INSERT INTO GROUP_USERS (GROUP_NAME, USERNAME)  "
                          "SELECT ?, USERNAME FROM GROUP_USERS WHERE GROUP_NAME = ?", (copy_name, group_name,))

        db.conn.commit()

    @property
    def db_first_group_name(self) -> str:
        """Just get a group, I don't care which"""
        db.cursor.execute("SELECT NAME FROM GROUPS")
        return db.cursor.fetchone()[0]

    @property
    def db_group_count(self):
        db.cursor.execute("SELECT COUNT(*) FROM GROUPS")
        return db.cursor.fetchone()[0]

    def db_get_sess(self, sess_name: str):
        if sess_id := self.db_get_sessid(sess_name):
            return sa.login_by_id(sess_id)
        return None


ctx = _Ctx()
console = rich.console.Console()
