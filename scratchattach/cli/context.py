"""
Handles data like current session for 'sessionable' commands.
Also provides wrappers for some SQL info
"""
import argparse
from dataclasses import dataclass, field
from typing_extensions import Optional

from scratchattach.cli.namespace import ArgSpace
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

ctx = _Ctx()
