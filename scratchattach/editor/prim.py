from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Optional, Callable, Final

from . import base, sprite, vlb, commons, build_defaulting
from ..utils import enums, exceptions


@dataclass(init=True, repr=True)
class PrimType(base.JSONSerializable):
    code: int
    name: str
    attrs: list = None
    opcode: str = None

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other
        elif isinstance(other, enums._EnumWrapper):
            other = other.value
        return super().__eq__(other)

    @staticmethod
    def from_json(data: int):
        return PrimTypes.find(data, "code")

    def to_json(self) -> int:
        return self.code


BASIC_ATTRS: Final[tuple[str]] = ("value",)
VLB_ATTRS: Final[tuple[str]] = ("name", "id", "x", "y")


class PrimTypes(enums._EnumWrapper):
    # Yeah, they actually do have opcodes
    NUMBER = PrimType(4, "number", BASIC_ATTRS, "math_number")
    POSITIVE_NUMBER = PrimType(5, "positive number", BASIC_ATTRS, "math_positive_number")
    POSITIVE_INTEGER = PrimType(6, "positive integer", BASIC_ATTRS, "math_whole_number")
    INTEGER = PrimType(7, "integer", BASIC_ATTRS, "math_integer")
    ANGLE = PrimType(8, "angle", BASIC_ATTRS, "math_angle")
    COLOR = PrimType(9, "color", BASIC_ATTRS, "colour_picker")
    STRING = PrimType(10, "string", BASIC_ATTRS, "text")
    BROADCAST = PrimType(11, "broadcast", VLB_ATTRS, "event_broadcast_menu")
    VARIABLE = PrimType(12, "variable", VLB_ATTRS, "data_variable")
    LIST = PrimType(13, "list", VLB_ATTRS, "data_listcontents")

    @classmethod
    def find(cls, value, by: str, apply_func: Optional[Callable] = None) -> PrimType:
        return super().find(value, by, apply_func=apply_func)


def is_prim_opcode(opcode: str):
    return opcode in PrimTypes.all_of("opcode") and opcode is not None


class Prim(base.SpriteSubComponent):
    def __init__(self, _primtype: PrimType | PrimTypes, _value: Optional[str | vlb.Variable | vlb.List | vlb.Broadcast] = None,
                 _name: Optional[str] = None, _id: Optional[str] = None, _x: Optional[int] = None,
                 _y: Optional[int] = None, _sprite: sprite.Sprite = build_defaulting.SPRITE_DEFAULT):
        """
        Class representing a Scratch string, number, angle, variable etc.
        Technically blocks but behave differently
        https://en.scratch-wiki.info/wiki/Scratch_File_Format#Targets:~:text=A%20few%20blocks,13
        """
        if isinstance(_primtype, PrimTypes):
            _primtype = _primtype.value

        self.type = _primtype

        self.value = _value

        self.name = _name
        """
        Once you get the object associated with this primitive (sprite.link_prims()), 
        the name will be removed and the value will be changed from ``None``
        """
        self.value_id = _id
        """
        It's not an object accessed by id, but it may reference an object with an id.
        
        ----
        
        Once you get the object associated with it (sprite.link_prims()), 
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

        _value, _name, _value_id, _x, _y = (None,) * 5
        if _prim_type.attrs == BASIC_ATTRS:
            assert len(data) == 2
            _value = data[1]

        elif _prim_type.attrs == VLB_ATTRS:
            assert len(data) in (3, 5)
            _name, _value_id = data[1:3]

            if len(data) == 5:
                _x, _y = data[3:]

        return Prim(_prim_type, _value, _name, _value_id, _x, _y)

    def to_json(self) -> list:
        if self.type.attrs == BASIC_ATTRS:
            return [self.type.code, self.value]
        else:
            return commons.trim_final_nones([self.type.code, self.value.name, self.value.id, self.x, self.y])

    def link_using_sprite(self):
        # Link prim to var/list/broadcast
        if self.is_vlb:
            if self.type.name == "variable":
                self.value = self.sprite.find_variable(self.value_id, "id")

            elif self.type.name == "list":
                self.value = self.sprite.find_list(self.value_id, "id")

            elif self.type.name == "broadcast":
                self.value = self.sprite.find_broadcast(self.value_id, "id")
            else:
                # This should never happen
                raise exceptions.BadVLBPrimitiveError(f"{self} claims to be VLB, but is {self.type.name}")

            if self.value is None:
                if not self.project:
                    new_vlb = vlb.construct(self.type.name.lower(), self.value_id, self.name)
                    self.sprite.add_local_global(new_vlb)
                    self.value = new_vlb

                else:
                    new_vlb = vlb.construct(self.type.name.lower(), self.value_id, self.name)
                    self.sprite.stage.add_vlb(new_vlb)

                    warnings.warn(
                        f"Prim<name={self.name!r}, id={self.name!r}> has unknown {self.type.name} id; adding as global variable")
            self.name = None
            self.value_id = None

    @property
    def can_next(self):
        return False
