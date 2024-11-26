from __future__ import annotations

import warnings

from . import base, sprite, mutation, field, inputs, commons


class Block(base.SpriteSubComponent):
    def __init__(self, _opcode: str, _shadow: bool = False, _top_level: bool = False,
                 _mutation: mutation.Mutation = None, _fields: dict[str, field.Field] = None,
                 _inputs: dict[str, inputs.Input] = None, x: int = None, y: int = None,

                 _next: Block = None, _parent: Block = None,
                 *, _next_id: str = None, _parent_id: str = None, _sprite: sprite.Sprite = None):
        # Defaulting for args
        if _fields is None:
            _fields = {}
        if _inputs is None:
            _inputs = {}

        self.opcode = _opcode
        self.is_shadow = _shadow
        self.is_top_level = _top_level

        self.x, self.y = x, y

        self.mutation = _mutation
        self.fields = _fields
        self.inputs = _inputs

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

        for iterable in (self.fields.values(), self.inputs.values()):
            for subcomponent in iterable:
                subcomponent.block = self

    def __repr__(self):
        return f"Block<{self.opcode!r}>"

    @property
    def id(self) -> str | None:
        # warnings.warn(f"Using block IDs can cause consistency issues and is not recommended")
        # This property is used when converting comments to JSON (we don't want random warning when exporting a project)
        for _block_id, _block in self.sprite.blocks.items():
            if _block is self:
                return _block_id

    @property
    def parent_id(self):
        if self.parent is not None:
            return self.parent.id
        else:
            return None

    @property
    def next_id(self):
        if self.next is not None:
            return self.next.id
        else:
            return None

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
            _inputs[_input_code] = inputs.Input.from_json(_input_data)

        _fields = {}
        for _field_code, _field_data in data.get("fields", {}).items():
            _fields[_field_code] = field.Field.from_json(_field_data)

        if "mutation" in data:
            _mutation = mutation.Mutation.from_json(data["mutation"])
        else:
            _mutation = None

        _x, _y = data.get("x"), data.get("y")

        return Block(_opcode, _shadow, _top_level, _mutation, _fields, _inputs, _x, _y, _next_id=_next_id,
                     _parent_id=_parent_id)

    def to_json(self) -> dict:
        _json = {
            "opcode": self.opcode,
            "next": self.next_id,
            "parent": self.parent_id,
            "inputs": {_id: _input.to_json() for _id, _input in self.inputs.items()},
            "fields": {_id: _field.to_json() for _id, _field in self.fields.items()},
            "shadow": self.is_shadow,
            "topLevel": self.is_top_level,
        }

        commons.noneless_update(_json, {
            "x": self.x,
            "y": self.y,
        })

        if self.mutation is not None:
            commons.noneless_update(_json, {
                "mutation": self.mutation.to_json(),
            })

        return _json

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

        for _field in self.fields.values():
            if _field.id is not None:
                new_value = self.sprite.find_vlb(_field.id, "id")
                if new_value is None:
                    warnings.warn(f"Could not find {_field.id!r} in {self}")
                else:
                    _field.value = new_value
                    _field.id = None

        for _input in self.inputs.values():
            _input.link_using_block()
