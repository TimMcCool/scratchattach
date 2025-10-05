import argparse
from typing_extensions import Optional, Literal


class ArgSpace(argparse.Namespace):
    command: Optional[Literal['login', 'group']]
    sessid: bool | str

    group_command: Optional[Literal['list', 'new', 'switch', 'add']]
    group_name: str
