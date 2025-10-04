import argparse
from typing_extensions import Optional, Literal


class ArgSpace(argparse.Namespace):
    command: Optional[Literal['login', 'group']]
    sessid: bool | str
