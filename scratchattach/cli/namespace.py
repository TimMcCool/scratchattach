import argparse
from typing_extensions import Optional, Literal


class ArgSpace(argparse.Namespace):
    command: Literal['login', 'group', 'profile', 'sessions'] | None
    sessid: bool | str
    username: str | None
    studio_id: str | None
    project_id: str | None
    session_name: str | None

    group_command: Literal['list', 'new', 'switch', 'add', 'remove',  'delete', 'copy', 'rename'] | None
    group_name: str
