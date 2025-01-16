"""
Editor base classes
"""

from __future__ import annotations

import copy
import json
from abc import ABC, abstractmethod
from io import TextIOWrapper
from typing import Optional, Any, TYPE_CHECKING, BinaryIO

if TYPE_CHECKING:
    from . import project, sprite, block, mutation, asset

from . import build_defaulting


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


class JSONExtractable(JSONSerializable, ABC):
    @staticmethod
    @abstractmethod
    def load_json(data: str | bytes | TextIOWrapper | BinaryIO, load_assets: bool = True, _name: Optional[str] = None) -> tuple[
        str, list[asset.AssetFile], str]:
        """
        Automatically extracts the JSON data as a string, as well as providing auto naming
        :param data: Either a string of JSON, sb3 file as bytes or as a file object
        :param load_assets: Whether to extract assets as well (if applicable)
        :param _name: Any provided name (will automatically find one otherwise)
        :return: tuple of the name, asset data & json as a string
        """
        ...


class ProjectSubcomponent(JSONSerializable, ABC):
    def __init__(self, _project: Optional[project.Project] = None):
        self.project = _project


class SpriteSubComponent(JSONSerializable, ABC):
    def __init__(self, _sprite: sprite.Sprite = build_defaulting.SPRITE_DEFAULT):
        if _sprite is build_defaulting.SPRITE_DEFAULT:
            _sprite = build_defaulting.current_sprite()

        self.sprite = _sprite

    # @property
    # def sprite(self):
    #     if self._sprite is None:
    #         print("ok, ", build_defaulting.current_sprite())
    #         return build_defaulting.current_sprite()
    #     else:
    #         return self._sprite

    # @sprite.setter
    # def sprite(self, value):
    #     self._sprite = value

    @property
    def project(self) -> project.Project:
        return self.sprite.project


class IDComponent(SpriteSubComponent, ABC):
    def __init__(self, _id: str, _sprite: sprite.Sprite = build_defaulting.SPRITE_DEFAULT):
        self.id = _id
        super().__init__(_sprite)

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.id}>"


class NamedIDComponent(IDComponent, ABC):
    """
    Base class for Variables, Lists and Broadcasts (Name + ID + sprite)
    """

    def __init__(self, _id: str, name: str, _sprite: sprite.Sprite = build_defaulting.SPRITE_DEFAULT):
        self.name = name
        super().__init__(_id, _sprite)

    def __repr__(self):
        return f"<{self.__class__.__name__} '{self.name}'>"


class BlockSubComponent(JSONSerializable, ABC):
    def __init__(self, _block: Optional[block.Block] = None):
        self.block = _block

    @property
    def sprite(self) -> sprite.Sprite:
        return self.block.sprite

    @property
    def project(self) -> project.Project:
        return self.sprite.project


class MutationSubComponent(JSONSerializable, ABC):
    def __init__(self, _mutation: Optional[mutation.Mutation] = None):
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
