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

    @property
    def current_group_name(self):
        return db.cursor \
            .execute("SELECT * FROM CURRENT WHERE GROUP_NAME IS NOT NULL") \
            .fetchone()[0]


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
