"""
Editor base classes
"""

from __future__ import annotations

import copy
import json
from abc import ABC, abstractmethod
from io import TextIOWrapper
from typing import Optional, Any, TYPE_CHECKING, BinaryIO, Union

if TYPE_CHECKING:
    from . import project, block, asset
    from . import mutation as module_mutation
    from . import sprite as module_sprite
    from . import commons

from . import build_defaulting


class Base(ABC):
    """
    Abstract base class for most sa.editor classes. Implements copy functions
    """
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
    """
    'Interface' for to_json() and from_json() methods
    Also implements save_json() using to_json()
    """
    @staticmethod
    @abstractmethod
    def from_json(data):
        pass

    @abstractmethod
    def to_json(self):
        pass

    def save_json(self, name: str = ''):
        """
        Save json to a file. Adds '.json' for you.
        """
        data = self.to_json()
        with open(f"{self.__class__.__name__.lower()}{name}.json", "w") as f:
            json.dump(data, f)


class JSONExtractable(JSONSerializable, ABC):
    """
    Interface for objects that can be loaded from zip archives containing json files (sprite/project)
    Only has one method - load_json
    """
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


class ProjectSubcomponent(JSONSerializable, ABC):
    """
    Base class for any class with an associated project
    """
    def __init__(self, _project: Optional[project.Project] = None):
        self.project = _project


class SpriteSubComponent(JSONSerializable, ABC):
    """
    Base class for any class with an associated sprite
    """
    sprite: module_sprite.Sprite
    def __init__(self, _sprite: "commons.SpriteInput" = build_defaulting.SPRITE_DEFAULT):
        if _sprite is build_defaulting.SPRITE_DEFAULT:
            _sprite = build_defaulting.current_sprite()
        self.sprite = _sprite

    @property
    def project(self) -> project.Project:
        """
        Get associated project by proxy of the associated sprite
        """
        p = self.sprite.project
        assert p is not None
        return p


class IDComponent(SpriteSubComponent, ABC):
    """
    Base class for classes with an id attribute
    """
    def __init__(self, _id: str, _sprite: "commons.SpriteInput" = build_defaulting.SPRITE_DEFAULT):
        self.id = _id
        super().__init__(_sprite)

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.id}>"


class NamedIDComponent(IDComponent, ABC):
    """
    Base class for Variables, Lists and Broadcasts (Name + ID + sprite)
    """
    def __init__(self, _id: str, name: str, _sprite: "commons.SpriteInput" = build_defaulting.SPRITE_DEFAULT):
        self.name = name
        super().__init__(_id, _sprite)

    def __repr__(self):
        return f"<{self.__class__.__name__} '{self.name}'>"


class BlockSubComponent(JSONSerializable, ABC):
    """
    Base class for classes with associated blocks
    """
    def __init__(self, _block: Optional[block.Block] = None):
        self.block = _block

    @property
    def sprite(self) -> module_sprite.Sprite:
        """
        Fetch sprite by proxy of the block
        """
        b = self.block
        assert b is not None
        return b.sprite

    @property
    def project(self) -> project.Project:
        """
        Fetch project by proxy of the sprite (by proxy of the block)
        """
        p = self.sprite.project
        assert p is not None
        return p


class MutationSubComponent(JSONSerializable, ABC):
    """
    Base class for classes with associated mutations
    """
    mutation: Optional[module_mutation.Mutation]
    def __init__(self, _mutation: Optional[module_mutation.Mutation] = None):
        self.mutation = _mutation

    @property
    def block(self) -> block.Block:
        """
        Fetch block by proxy of mutation
        """
        m = self.mutation
        assert m is not None
        b = m.block
        assert b is not None
        return b

    @property
    def sprite(self) -> module_sprite.Sprite:
        """
        Fetch sprite by proxy of block (by proxy of mutation)
        """
        return self.block.sprite

    @property
    def project(self) -> project.Project:
        """
        Fetch project by proxy of sprite (by proxy of block (by proxy of mutation))
        """
        p = self.sprite.project
        assert p is not None
        return p
