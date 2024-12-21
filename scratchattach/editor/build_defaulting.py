"""
Module which stores the 'default' or 'current' selected Sprite/project (stored as a stack) which makes it easier to write scratch code directly in Python
"""
from __future__ import annotations

from typing import Iterable, TYPE_CHECKING, Final

if TYPE_CHECKING:
    from . import sprite, block, prim, comment
from . import commons


class _SetSprite(commons.Singleton):
    def __repr__(self):
        return f'<Reminder to default your sprite to {current_sprite()}>'


SPRITE_DEFAULT: Final[_SetSprite] = _SetSprite()

_sprite_stack: list[sprite.Sprite] = []


def stack_add_sprite(_sprite: sprite.Sprite):
    _sprite_stack.append(_sprite)


def current_sprite() -> sprite.Sprite | None:
    if len(_sprite_stack) == 0:
        return None
    return _sprite_stack[-1]


def pop_sprite(_sprite: sprite.Sprite) -> sprite.Sprite | None:
    assert _sprite_stack.pop() == _sprite
    return _sprite


def add_block(_block: block.Block | prim.Prim) -> block.Block | prim.Prim:
    return current_sprite().add_block(_block)


def add_chain(*chain: Iterable[block.Block, prim.Prim]) -> block.Block | prim.Prim:
    return current_sprite().add_chain(*chain)


def add_comment(_comment: comment.Comment):
    return current_sprite().add_comment(_comment)
