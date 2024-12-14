"""
Editor base classes
"""

from __future__ import annotations

import copy
import json
from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from . import project
    from . import sprite
    from . import block
    from . import mutation


class Base(ABC):
    def dcopy(self):
        """
        :return: A **deep** copy of self
        """
        return copy.deepcopy(self)

    def copy(self):
        """
        :return: A **shallow** copy of self
        """
        return copy.copy(self)


class JSONSerializable(Base, ABC):
    @staticmethod
    @abstractmethod
    def from_json(data: dict | list | Any):
        pass

    @abstractmethod
    def to_json(self) -> dict | list | Any:
        pass

    def save_json(self, name: str = ''):
        data = self.to_json()
        with open(f"{self.__class__.__name__.lower()}{name}.json", "w") as f:
            json.dump(data, f)


class ProjectSubcomponent(JSONSerializable, ABC):
    def __init__(self, _project: project.Project = None):
        self.project = _project


class SpriteSubComponent(JSONSerializable, ABC):
    def __init__(self, _sprite: sprite.Sprite = None):
        self.sprite = _sprite

    @property
    def project(self) -> project.Project:
        return self.sprite.project


class IDComponent(SpriteSubComponent, ABC):
    def __init__(self, _id: str, _sprite: sprite.Sprite = None):
        self.id = _id
        super().__init__(_sprite)

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.id}>"


class NamedIDComponent(IDComponent, ABC):
    """
    Base class for Variables, Lists and Broadcasts (Name + ID + sprite)
    """

    def __init__(self, _id: str, name: str, _sprite: sprite.Sprite = None):
        self.name = name
        super().__init__(_id, _sprite)

    def __repr__(self):
        return f"<{self.__class__.__name__} '{self.name}'>"


class BlockSubComponent(JSONSerializable, ABC):
    def __init__(self, _block: block.Block = None):
        self.block = _block

    @property
    def sprite(self) -> sprite.Sprite:
        return self.block.sprite

    @property
    def project(self) -> project.Project:
        return self.sprite.project


class MutationSubComponent(JSONSerializable, ABC):
    def __init__(self, _mutation: mutation.Mutation = None):
        self.mutation = _mutation

    @property
    def block(self) -> block.Block:
        return self.mutation.block

    @property
    def sprite(self) -> sprite.Sprite:
        return self.block.sprite

    @property
    def project(self) -> project.Project:
        return self.sprite.project
