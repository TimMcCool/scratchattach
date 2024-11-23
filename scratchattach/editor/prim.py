from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Final

from . import base, sprite
from ..utils import enums


@dataclass(init=True, repr=True)
class PrimType(base.ProjectPart):
    code: int
    name: str
    attrs: list = None

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other
        elif isinstance(other, enums._EnumWrapper):
            other = other.value
        return super().__eq__(other)

    @staticmethod
    def from_json(data: int):
        pass

    def to_json(self) -> int:
        pass


BASIC_ATTRS: Final = ["value"]
VLB_ATTRS: Final = ["name", "id", "x", "y"]


class PrimTypes(enums._EnumWrapper):
    NULL = PrimType(1, "null")
    BLOCK = PrimType(2, "block")
    NUMBER = PrimType(4, "number", BASIC_ATTRS)
    POSITIVE_NUMBER = PrimType(5, "positive number", BASIC_ATTRS)
    POSITIVE_INTEGER = PrimType(6, "positive integer", BASIC_ATTRS)
    INTEGER = PrimType(7, "integer", BASIC_ATTRS)
    ANGLE = PrimType(8, "angle", BASIC_ATTRS)
    COLOR = PrimType(9, "color", BASIC_ATTRS)
    STRING = PrimType(10, "string", BASIC_ATTRS)
    BROADCAST = PrimType(11, "broadcast", VLB_ATTRS)
    VARIABLE = PrimType(12, "variable", VLB_ATTRS)
    LIST = PrimType(13, "list", VLB_ATTRS)

    @classmethod
    def find(cls, value, by: str, apply_func: Callable = None) -> PrimType:
        return super().find(value, by, apply_func=apply_func)


class Prim(base.SpriteSubComponent):
    def __init__(self, _primtype: PrimType, _value: str = None, _name: str = None, _id: str = None, _x: int = None,
                 _y: int = None, _sprite: sprite.Sprite = None):
        """
        Class representing a Scratch string, number, angle, variable etc.
        Technically blocks but behave differently
        https://en.scratch-wiki.info/wiki/Scratch_File_Format#Targets:~:text=A%20few%20blocks,13
        """
        self.type = _primtype

        self.value = _value

        self.name = _name
        """
        Once you get the object associated with this primitive (done upon sprite initialisation), 
        the name will be removed and the value will be changed from ``None``
        """
        self.id = _id
        """
        It's not an object accessed by id, but it may reference an object with an id.
        
        ----
        
        Once you get the object associated with it (done upon sprite initialisation), 
        the id will be removed and the value will be changed from ``None``
        """

        self.x = _x
        self.y = _y

        super().__init__(_sprite)

    def __repr__(self):
        if self.is_basic:
            return f"Prim<{self.type.name}: {self.value}>"
        elif self.is_vlb:
            return f"Prim<{self.type.name}: {self.value}>"
        else:
            return f"Prim<{self.type.name}>"

    @property
    def is_vlb(self):
        return self.type.attrs == VLB_ATTRS

    @property
    def is_basic(self):
        return self.type.attrs == BASIC_ATTRS

    @staticmethod
    def from_json(data: list):
        assert isinstance(data, list)

        _type_idx = data[0]
        _prim_type = PrimTypes.find(_type_idx, "code")

        _value, _name, _id, _x, _y = (None,) * 5
        if _prim_type == PrimTypes.NULL:
            pass
        elif _prim_type == PrimTypes.BLOCK:
            pass

        elif _prim_type.attrs == BASIC_ATTRS:
            assert len(data) == 2
            _value = data[1]

        elif _prim_type.attrs == VLB_ATTRS:
            assert len(data) in (3, 5)
            _name, _id = data[1:3]

            if len(data) == 5:
                _x, _y = data[3:5]

        return Prim(_prim_type, _value, _name, _id, _x, _y)

    def to_json(self) -> list:
        pass
