from __future__ import annotations

from . import base, sprite


class Block(base.IDComponent):
    def __init__(self, _id: str = None, _sprite: sprite.Sprite = None):
        super().__init__(_id, _sprite)

    @staticmethod
    def from_json(data: dict):
        pass

    def to_json(self) -> dict:
        pass
