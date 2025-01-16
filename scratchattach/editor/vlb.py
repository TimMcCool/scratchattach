"""
Variables, lists & broadcasts
"""
# Perhaps ids should not be stored in these objects, but in the sprite, similarly
# to how blocks/prims are stored

from __future__ import annotations

from typing import Optional, Literal

from . import base, sprite, build_defaulting
from ..utils import exceptions


class Variable(base.NamedIDComponent):
    def __init__(self, _id: str, _name: str, _value: Optional[str | int | float] = None, _is_cloud: bool = False,
                 _sprite: sprite.Sprite = build_defaulting.SPRITE_DEFAULT):
        """
        Class representing a variable.
        https://en.scratch-wiki.info/wiki/Scratch_File_Format#Targets:~:text=variables,otherwise%20not%20present
        """
        if _value is None:
            _value = 0

        self.value = _value
        self.is_cloud = _is_cloud

        super().__init__(_id, _name, _sprite)

    @property
    def is_global(self):
        """
        Works out whethere a variable is global based on whether the sprite is a stage
        :return: Whether this variable is a global variable.
        """
        return self.sprite.is_stage

    @staticmethod
    def from_json(data: tuple[str, tuple[str, str | int | float] | tuple[str, str | int | float, bool]]):
        """
        Read data in format: (variable id, variable JSON)
        """
        assert len(data) == 2
        _id, data = data

        assert len(data) in (2, 3)
        _name, _value = data[:2]

        if len(data) == 3:
            _is_cloud = data[2]
        else:
            _is_cloud = False

        return Variable(_id, _name, _value, _is_cloud)

    def to_json(self) -> tuple[str, str | int | float, bool] | tuple[str, str | int | float]:
        """
        Returns Variable data as a tuple
        """
        if self.is_cloud:
            _ret = self.name, self.value, True
        else:
            _ret = self.name, self.value

        return _ret


class List(base.NamedIDComponent):
    def __init__(self, _id: str, _name: str, _value: Optional[list[str | int | float]] = None,
                 _sprite: sprite.Sprite = build_defaulting.SPRITE_DEFAULT):
        """
        Class representing a list.
        https://en.scratch-wiki.info/wiki/Scratch_File_Format#Targets:~:text=lists,as%20an%20array
        """
        if _value is None:
            _value = []

        self.value = _value
        super().__init__(_id, _name, _sprite)

    @staticmethod
    def from_json(data: tuple[str, tuple[str, str | int | float] | tuple[str, str | int | float, bool]]):
        """
        Read data in format: (variable id, variable JSON)
        """
        assert len(data) == 2
        _id, data = data

        assert len(data) == 2
        _name, _value = data

        return List(_id, _name, _value)

    def to_json(self) -> tuple[str, tuple[str, str | int | float, bool] | tuple[str, str | int | float]]:
        """
        Returns List data as a tuple
        """
        return self.name, self.value


class Broadcast(base.NamedIDComponent):
    def __init__(self, _id: str, _name: str, _sprite: sprite.Sprite = build_defaulting.SPRITE_DEFAULT):
        """
        Class representing a broadcast.
        https://en.scratch-wiki.info/wiki/Scratch_File_Format#Targets:~:text=broadcasts,in%20the%20stage
        """
        super().__init__(_id, _name, _sprite)

    @staticmethod
    def from_json(data: tuple[str, str]):
        assert len(data) == 2
        _id, _name = data

        return Broadcast(_id, _name)

    def to_json(self) -> str:
        """
        :return: Broadcast as JSON (just a string of its name)
        """
        return self.name


def construct(vlb_type: Literal["variable", "list", "broadcast"], _id: Optional[str] = None, _name: Optional[str] = None,
              _sprite: sprite.Sprite = build_defaulting.SPRITE_DEFAULT) -> Variable | List | Broadcast:
    if vlb_type == "variable":
        vlb_type = Variable
    elif vlb_type == "list":
        vlb_type = List
    elif vlb_type == "broadcast":
        vlb_type = Broadcast
    else:
        raise exceptions.InvalidVLBName(f"Bad VLB {vlb_type!r}")

    return vlb_type(_id, _name, _sprite)
