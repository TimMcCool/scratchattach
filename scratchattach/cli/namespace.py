import argparse
from typing_extensions import Optional, Literal


class ArgSpace(argparse.Namespace):
    command: Optional[Literal['login', 'group', 'profile', 'sessions']]
    sessid: bool | str
    username: Optional[str]
    studio_id: Optional[str]
    project_id: Optional[str]
    session_name: Optional[str]

    group_command: Optional[Literal['list', 'new', 'switch', 'add', 'remove',  'delete', 'copy', 'rename']]
    group_name: str
