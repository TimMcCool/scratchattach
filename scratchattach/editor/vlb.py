"""
Variables, lists & broadcasts
"""

from __future__ import annotations

from . import base, sprite


class Variable(base.NamedIDComponent):
    def __init__(self, _id: str, _name: str, _value: str | int | float, _is_cloud: bool = False,
                 _sprite: sprite.Sprite = None):
        """
        Class representing a variable.
        https://en.scratch-wiki.info/wiki/Scratch_File_Format#Targets:~:text=variables,otherwise%20not%20present
        """
        self.value = _value
        self.is_cloud = _is_cloud

        super().__init__(_id, _name, _sprite)

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

    def to_json(self) -> tuple[str, tuple[str, str | int | float, bool] | tuple[str, str | int | float]]:
        """
        Returns Variable data as the variable id, then a tuple representing it
        """
        if self.is_cloud:
            _ret = self.name, self.value, True
        else:
            _ret = self.name, self.value

        return self.id, _ret


class List(base.NamedIDComponent):
    def __init__(self, _id: str, _name: str, _value: str | int | float,
                 _sprite: sprite.Sprite = None):
        """
        Class representing a list.
        https://en.scratch-wiki.info/wiki/Scratch_File_Format#Targets:~:text=lists,as%20an%20array
        """
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
        Returns List data as the list id, then a tuple representing it
        """
        return self.id, (self.name, self.value)


class Broadcast(base.NamedIDComponent):
    def __init__(self, _id: str, _name: str, _sprite: sprite.Sprite = None):
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

    def to_json(self) -> tuple[str, str]:
        return self.id, self.name
