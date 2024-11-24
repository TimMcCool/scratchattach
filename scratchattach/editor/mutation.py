from __future__ import annotations

import json
from dataclasses import dataclass
from typing import TYPE_CHECKING

from . import base
from ..utils import enums

if TYPE_CHECKING:
    from . import block


@dataclass(init=True)
class ArgumentPlaceholder(base.Base):
    type: str

    def __eq__(self, other):
        if isinstance(other, enums._EnumWrapper):
            other = other.value

        assert isinstance(other, ArgumentPlaceholder)

        return self.type == other.type

    def __repr__(self):
        return f"<Arg {self.type!r}>"


class ArgumentPlaceholders(enums._EnumWrapper):
    BOOLEAN = ArgumentPlaceholder("boolean")
    NUMBER_OR_TEXT = ArgumentPlaceholder("number or text")


def parse_proc_code(_proc_code: str) -> list[str, ArgumentPlaceholder] | None:
    if _proc_code is None:
        return None
    token = ''
    tokens = []

    last_char = ''
    for char in _proc_code:
        if last_char == '%':
            if char in "sb":
                # If we've hit an %s or %b
                token = token[:-1]
                # Clip the % sign off the token

                if token != '':
                    # Make sure not to append an empty token
                    tokens.append(token)

                # Add the parameter token
                token = f"%{char}"
                if token == "%b":
                    tokens.append(ArgumentPlaceholder("boolean"))
                elif token == "%s":
                    tokens.append(ArgumentPlaceholder("number or text"))

                token = ''
                continue

        token += char
        last_char = char

    if token != '':
        tokens.append(token)

    return tokens


@dataclass(init=True, repr=True)
class ArgSettings(base.Base):
    ids: bool
    names: bool
    defaults: bool

    def __int__(self):
        return (int(self.ids) +
                int(self.names) +
                int(self.defaults))

    def __eq__(self, other):
        return (self.ids == other.ids and
                self.names == other.names and
                self.defaults == other.defaults)

    def __gt__(self, other):
        return int(self) > int(other)

    def __lt__(self, other):
        return int(self) > int(other)


@dataclass(init=True, repr=True)
class Argument(base.Base):
    name: str
    default: str = ''

    _id: str = None
    """
    Argument ID: Will be used to replace other parameters during block instantiation.
    """

    _block: block.Block = None


class Mutation(base.BlockSubComponent):
    def __init__(self, _tag_name: str = "mutation", _children: list = None, _proc_code: str = None,
                 _is_warp: bool = None, _arguments: list[Argument] = None, _has_next: bool = None,
                 _argument_settings: ArgSettings = None, *,
                 _block: block.Block = None):
        """
        Mutation for Control:stop block and procedures
        https://en.scratch-wiki.info/wiki/Scratch_File_Format#Mutations
        """
        # Defaulting for args
        if _children is None:
            _children = []
        if _argument_settings is None:
            if _arguments:
                _argument_settings = ArgSettings(
                    _arguments[0]._id is None,
                    _arguments[0].name is None,
                    _arguments[0].default is None
                )
            else:
                _argument_settings = ArgSettings(False, False, False)

        self.tag_name = _tag_name
        self.children = _children

        self.proc_code = _proc_code
        self.is_warp = _is_warp
        self.arguments = _arguments
        self.og_argument_settings = _argument_settings

        self.has_next = _has_next

        super().__init__(_block)

    def __repr__(self):
        if self.arguments is not None:
            return f"Mutation<args={self.arguments}>"
        else:
            return f"Mutation<hasnext={self.has_next}>"

    @property
    def argument_ids(self):
        if self.arguments is not None:
            return [_arg._id for _arg in self.arguments]
        else:
            return None

    @property
    def argument_names(self):
        if self.arguments is not None:
            return [_arg.name for _arg in self.arguments]
        else:
            return None

    @property
    def argument_defaults(self):
        if self.arguments is not None:
            return [_arg.default for _arg in self.arguments]
        else:
            return None

    @property
    def argument_settings(self) -> ArgSettings:
        return ArgSettings(bool(self.argument_ids),
                           bool(self.argument_names),
                           bool(self.argument_defaults))

    @property
    def parsed_proc_code(self) -> list[str, ArgumentPlaceholder] | None:
        return parse_proc_code(self.proc_code)

    @staticmethod
    def from_json(data: dict) -> Mutation:
        assert isinstance(data, dict)

        _tag_name = data.get("tagName", "mutation")
        _children = data.get("children", [])

        # procedures_prototype & procedures_call attrs
        _proc_code = data.get("proccode")
        _is_warp = data.get("warp")

        _argument_ids = data.get("argumentids")
        # For some reason these are stored as JSON strings
        if _argument_ids is not None:
            _argument_ids = json.loads(_argument_ids)

        # procedures_prototype attrs
        _argument_names = data.get("argumentnames")
        _argument_defaults = data.get("argumentdefaults")
        # For some reason these are stored as JSON strings
        if _argument_names is not None:
            assert isinstance(_argument_names, str)
            _argument_names = json.loads(_argument_names)
        if _argument_defaults is not None:
            assert isinstance(_argument_defaults, str)
            _argument_defaults = json.loads(_argument_defaults)
        _argument_settings = ArgSettings(_argument_ids is not None,
                                         _argument_names is not None,
                                         _argument_defaults is not None)

        # control_stop attrs
        _has_next = data.get("hasnext")

        def get(_lst: list | tuple | None, _idx: int):
            if _lst is None:
                return None

            if len(_lst) <= _idx:
                return None
            else:
                return _lst[_idx]

        if _argument_ids is None:
            _arguments = None
        else:
            _arguments = []
            for i, _arg_id in enumerate(_argument_ids):
                _arg_name = get(_argument_names, i)
                _arg_default = get(_argument_defaults, i)

                _arguments.append(Argument(_arg_name, _arg_default, _arg_id))

        return Mutation(_tag_name, _children, _proc_code, _is_warp, _arguments, _has_next, _argument_settings)

    def to_json(self) -> dict | None:
        pass

    def link_arguments(self):
        if self.arguments is None:
            return

        # You only need to fetch argument data if you actually have arguments
        if len(self.arguments) > 0:
            if self.arguments[0].name is None:
                # This requires linking
                _proc_uses = self.sprite.find_block(self.argument_ids, "argument ids", True)
                # Note: Sometimes there may not be any argument ids provided. There will be no way to find out the names
                # Technically, defaults can be found by using the proc code
                for _use in _proc_uses:
                    if _use.mutation.argument_settings > self.argument_settings:
                        self.arguments = _use.mutation.arguments

                        if int(self.argument_settings) == 3:
                            # If all of our argument data is filled, we can stop early
                            break
