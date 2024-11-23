from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from . import base, sprite
from ..utils import enums


@dataclass(init=True, repr=True)
class PrimType(base.ProjectPart):
    code: int
    name: str

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other
        return super().__eq__(other)


    @staticmethod
    def from_json(data: int):
        pass

    def to_json(self) -> int:
        pass


class PrimTypes(enums._EnumWrapper):
    NULL = PrimType(1, "null")
    BLOCK = PrimType(2, "block")
    NUMBER = PrimType(4, "number")
    POSITIVE_NUMBER = PrimType(5, "positive number")
    POSITIVE_INTEGER = PrimType(6, "positive integer")
    INTEGER = PrimType(7, "integer")
    ANGLE = PrimType(8, "angle")
    COLOR = PrimType(9, "color")
    STRING = PrimType(10, "string")
    BROADCAST = PrimType(11, "broadcast")
    VARIABLE = PrimType(12, "variable")
    VAR = PrimType(12, "var")
    LIST = PrimType(13, "list")


class Primitive(base.IDComponent):
    def __init__(self, _id: str = None, _sprite: sprite.Sprite = None):
        """
        Class representing a Scratch string, number, angle etc.
        Technically blocks but behave differently
        https://en.scratch-wiki.info/wiki/Scratch_File_Format#Targets:~:text=A%20few%20blocks,13
        """
        super().__init__(_id, _sprite)

    @staticmethod
    def from_json(data: list):
        assert isinstance(data, list)

        _type_idx = data[0]
        _prim_type = PrimTypes.find(_type_idx, "code")
        print(_prim_type == "variable")

    def to_json(self) -> list:
        pass
