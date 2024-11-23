"""
Editor base classes
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from . import project
    from . import sprite


class ProjectPart(ABC):
    @staticmethod
    @abstractmethod
    def from_json(data: dict | list | Any):
        pass

    @abstractmethod
    def to_json(self) -> dict | list | Any:
        pass


class ProjectSubcomponent(ProjectPart, ABC):
    def __init__(self, _project: project.Project):
        self.project = _project


class SpriteSubComponent(ProjectPart, ABC):
    def __init__(self, _sprite: sprite.Sprite):
        self.sprite = _sprite

    @property
    def project(self) -> project.Project:
        return self.sprite.project


class IDComponent(SpriteSubComponent, ABC):
    def __init__(self, _id: str, _sprite: sprite.Sprite):
        self.id = _id
        super().__init__(_sprite)
