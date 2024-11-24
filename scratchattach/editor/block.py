from __future__ import annotations

import warnings

from . import base, sprite, mutation


class Block(base.SpriteSubComponent):
    def __init__(self, _opcode: str, _shadow: bool = False, _top_level: bool = False, _mutation: mutation.Mutation=None, _next: Block = None,
                 _parent: Block = None,
                 *, _next_id: str = None, _parent_id: str = None, _sprite: sprite.Sprite = None):

        self.opcode = _opcode
        self.is_shadow = _shadow
        self.is_top_level = _top_level

        self.mutation = _mutation

        self._next_id = _next_id
        """
        Temporarily stores id of next block. Will be used later during project instantiation to find the next block object
        """
        self._parent_id = _parent_id
        """
        Temporarily stores id of parent block. Will be used later during project instantiation to find the parent block object
        """

        self.next = _next
        self.parent = _parent

        super().__init__(_sprite)

        # Link subcomponents
        if self.mutation:
            self.mutation.block = self

    def __repr__(self):
        return f"Block<{self.opcode!r}>"

    @property
    def id(self) -> str | None:
        warnings.warn(f"Using block IDs can cause consistency issues and is not recommended")
        for _block_id, _block in self.sprite.blocks.items():
            if _block is self:
                return _block_id

    @property
    def relatives(self) -> list[Block]:
        """
        :return: A list of blocks which are related to this block (e.g. parent, next, inputs)
        """
        _ret = []

        def yield_block(_block: Block | None):
            if isinstance(_block, Block):
                _ret.append(_block)

        yield_block(self.next)
        yield_block(self.parent)

        return _ret

    @staticmethod
    def from_json(data: dict):
        _opcode = data["opcode"]

        _next_id = data.get("next")
        _parent_id = data.get("parent")

        _shadow = data.get("shadow", False)
        _top_level = data.get("topLevel", _parent_id is None)

        _inputs = {}
        for _input_code, _input_data in data.get("inputs", {}).items():
            _inputs[_input_code] = ...

        _fields = {}
        for _field_code, _field_data in data.get("fields", {}).items():
            _fields[_field_code] = ...

        if "mutation" in data:
            _mutation = mutation.Mutation.from_json(data["mutation"])
        else:
            _mutation = None

        return Block(_opcode, _shadow, _top_level, _mutation, _next_id=_next_id, _parent_id=_parent_id)

    def to_json(self) -> dict:
        pass

    def link_using_sprite(self):
        if self.mutation:
            self.mutation.link_arguments()

        if self._parent_id is not None:
            self.parent = self.sprite.find_block(self._parent_id, "id")
            if self.parent is not None:
                self._parent_id = None

        if self._next_id is not None:
            self.next = self.sprite.find_block(self._next_id, "id")
            if self.next is not None:
                self._next_id = None

        for _block in self.relatives:
            _block.sprite = self.sprite
