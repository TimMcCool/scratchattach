from __future__ import annotations

import warnings
from typing import Optional, Iterable, Self

from . import base, sprite, mutation, field, inputs, commons, vlb, blockshape, prim, comment, build_defaulting
from ..utils import exceptions


class Block(base.SpriteSubComponent):
    def __init__(self, _opcode: str, _shadow: bool = False, _top_level: Optional[bool] = None,
                 _mutation: Optional[mutation.Mutation] = None, _fields: Optional[dict[str, field.Field]] = None,
                 _inputs: Optional[dict[str, inputs.Input]] = None, x: int = 0, y: int = 0, pos: Optional[tuple[int, int]] = None,

                 _next: Optional[Block] = None, _parent: Optional[Block] = None,
                 *, _next_id: Optional[str] = None, _parent_id: Optional[str] = None, _sprite: sprite.Sprite = build_defaulting.SPRITE_DEFAULT):
        # Defaulting for args
        if _fields is None:
            _fields = {}
        if _inputs is None:
            _inputs = {}

        if pos is not None:
            x, y = pos

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

        self.check_toplevel()

        super().__init__(_sprite)
        self.link_subcomponents()

    def __repr__(self):
        return f"Block<{self.opcode!r}>"

    def link_subcomponents(self):
        if self.mutation:
            self.mutation.block = self

        for iterable in (self.fields.values(), self.inputs.values()):
            for subcomponent in iterable:
                subcomponent.block = self

    def add_input(self, name: str, _input: inputs.Input) -> Self:
        self.inputs[name] = _input
        for val in (_input.value, _input.obscurer):
            if isinstance(val, Block):
                val.parent = self
        return self

    def add_field(self, name: str, _field: field.Field) -> Self:
        self.fields[name] = _field
        return self

    def set_mutation(self, _mutation: mutation.Mutation) -> Self:
        self.mutation = _mutation
        _mutation.block = self
        _mutation.link_arguments()
        return self

    def set_comment(self, _comment: comment.Comment) -> Self:
        _comment.block = self
        self.sprite.add_comment(_comment)

        return self

    def check_toplevel(self):
        self.is_top_level = self.parent is None

        if not self.is_top_level:
            self.x, self.y = None, None

    @property
    def target(self):
        """
        Alias for sprite
        """
        return self.sprite

    @property
    def block_shape(self) -> blockshape.BlockShape:
        """
        Search for the blockshape stored in blockshape.py
        :return: The block's block shape (by opcode)
        """
        _shape = blockshape.BlockShapes.find(self.opcode, "opcode")
        if _shape is None:
            warnings.warn(f"No blockshape {self.opcode!r} exists! Defaulting to {blockshape.BlockShapes.UNDEFINED}")
            return blockshape.BlockShapes.UNDEFINED
        return _shape

    @property
    def can_next(self):
        """
        :return: Whether the block *can* have a next block (basically checks if it's not a cap block, also considering the behaviour of control_stop)
        """
        _shape = self.block_shape
        if _shape.is_cap is not blockshape.MUTATION_DEPENDENT:
            return _shape.is_attachable
        else:
            if self.mutation is None:
                # If there's no mutation, let's just assume yes
                warnings.warn(f"{self} has no mutation! Assuming we can add block ;-;")
                return True

            return self.mutation.has_next

    @property
    def id(self) -> str | None:
        """
        Work out the id of this block by searching through the sprite dictionary
        """
        # warnings.warn(f"Using block IDs can cause consistency issues and is not recommended")
        # This property is used when converting comments to JSON (we don't want random warning when exporting a project)
        for _block_id, _block in self.sprite.blocks.items():
            if _block is self:
                return _block_id

        # Let's just automatically assign ourselves an id
        self.sprite.add_block(self)

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

    @property
    def children(self) -> list[Block | prim.Prim]:
        """
        :return: A list of blocks that are inside of this block, **NOT INCLUDING THE ATTACHED BLOCK**
        """
        _children = []
        for _input in self.inputs.values():
            if isinstance(_input.value, Block) or isinstance(_input.value, prim.Prim):
                _children.append(_input.value)

            if _input.obscurer is not None:
                _children.append(_input.obscurer)
        return _children

    @property
    def previous_chain(self):
        if self.parent is None:
            return [self]

        return [self] + self.parent.previous_chain

    @property
    def attached_chain(self):
        if self.next is None:
            return [self]

        return [self] + self.next.attached_chain

    @property
    def complete_chain(self):
        # Both previous and attached chains start with self
        return self.previous_chain[:1:-1] + self.attached_chain

    @property
    def top_level_block(self):
        """
        same as the old stack_parent property from sbedtior v1
        """
        return self.previous_chain[-1]

    @property
    def bottom_level_block(self):
        return self.attached_chain[-1]

    @property
    def stack_tree(self):
        """
        :return: A tree-like nested list structure representing the stack of blocks, including inputs, starting at this block
        """
        _tree = [self]
        for child in self.children:
            if isinstance(child, prim.Prim):
                _tree.append(child)
            elif isinstance(child, Block):
                _tree.append(child.stack_tree)

        if self.next:
            _tree += self.next.stack_tree

        return _tree

    @property
    def category(self):
        """
        Works out what category of block this is using the opcode. Does not perform validation
        """
        return self.opcode.split('_')[0]

    @property
    def is_input(self):
        """
        :return: Whether this block is an input obscurer or value
        """
        return self.parent_input is not None

    @property
    def is_next_block(self):
        """
        :return: Whether this block is attached (as next block) to a previous block and not an input
        """
        return self.parent and not self.is_input

    @property
    def parent_input(self):
        if not self.parent:
            return None

        for _input in self.parent.inputs.values():
            if _input.obscurer is self or _input.value is self:
                return _input
        return None

    @property
    def new_id(self):
        return self.sprite.new_id

    @property
    def comment(self) -> comment.Comment | None:
        for _comment in self.sprite.comments:
            if _comment.block is self:
                return _comment
        return None

    @property
    def turbowarp_block_opcode(self):
        """
        :return: The 'opcode' if this is a turbowarp block: e.g.
        - log
        - breakpoint
        - error
        - warn
        - is compiled?
        - is turbowarp?
        - is forkphorus?
        If it's not one, just returns None
        """
        if self.opcode == "procedures_call":
            if self.mutation:
                if self.mutation.proc_code:
                    # \u200B is a zero-width space
                    if self.mutation.proc_code == "\u200B\u200Bbreakpoint\u200B\u200B":
                        return "breakpoint"
                    elif self.mutation.proc_code == "\u200B\u200Blog\u200B\u200B %s":
                        return "log"
                    elif self.mutation.proc_code == "\u200B\u200Berror\u200B\u200B %s":
                        return "error"
                    elif self.mutation.proc_code == "\u200B\u200Bwarn\u200B\u200B %s":
                        return "warn"

        elif self.opcode == "argument_reporter_boolean":
            arg = self.fields.get("VALUE")

            if arg is not None:
                arg = arg.value
                if isinstance(arg, str):
                    arg = arg.lower()

                    if arg == "is turbowarp?":
                        return "is_turbowarp?"

                    elif arg == "is compiled?":
                        return "is_compiled?"

                    elif arg == "is forkphorus?":
                        return "is_forkphorus?"

        return None

    @property
    def is_turbowarp_block(self):
        return self.turbowarp_block_opcode is not None

    @staticmethod
    def from_json(data: dict) -> Block:
        """
        Load a block from the JSON dictionary.
        :param data: a dictionary (not list)
        :return: The new Block object
        """
        _opcode = data["opcode"]

        _x, _y = data.get("x"), data.get("y")

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

        return Block(_opcode, _shadow, _top_level, _mutation, _fields, _inputs, _x, _y, _next_id=_next_id,
                     _parent_id=_parent_id)

    def to_json(self) -> dict:
        self.check_toplevel()

        _json = {
            "opcode": self.opcode,
            "next": self.next_id,
            "parent": self.parent_id,
            "inputs": {_id: _input.to_json() for _id, _input in self.inputs.items()},
            "fields": {_id: _field.to_json() for _id, _field in self.fields.items()},
            "shadow": self.is_shadow,
            "topLevel": self.is_top_level,
        }
        _comment = self.comment
        if _comment:
            commons.noneless_update(_json, {
                "comment": _comment.id
            })

        if self.is_top_level:
            commons.noneless_update(_json, {
                "x": self.x,
                "y": self.y,
            })

        if self.mutation is not None:
            commons.noneless_update(_json, {
                "mutation": self.mutation.to_json(),
            })

        return _json

    def link_using_sprite(self, link_subs: bool = True):
        if link_subs:
            self.link_subcomponents()

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
                    # We probably need to add a local global variable
                    _type = _field.type

                    if _type == field.Types.VARIABLE:
                        # Create a new variable
                        new_value = vlb.Variable(commons.gen_id(),
                                                 _field.value)
                    elif _type == field.Types.LIST:
                        # Create a list
                        new_value = vlb.List(commons.gen_id(),
                                             _field.value)
                    elif _type == field.Types.BROADCAST:
                        # Create a broadcast
                        new_value = vlb.Broadcast(commons.gen_id(),
                                                  _field.value)
                    else:
                        # Something probably went wrong
                        warnings.warn(
                            f"Could not find {_field.id!r} in {self.sprite}. Can't create a new {_type} so we gave a warning")

                    if new_value is not None:
                        self.sprite.add_local_global(new_value)

                # Check again since there may have been a newly created VLB
                if new_value is not None:
                    _field.value = new_value
                    _field.id = None

        for _input in self.inputs.values():
            _input.link_using_block()

    # Adding/removing block
    def attach_block(self, new: Block) -> Block:
        if not self.can_next:
            raise exceptions.BadBlockShape(f"{self.block_shape} cannot be stacked onto")
        elif new.block_shape.is_hat or not new.block_shape.is_stack:
            raise exceptions.BadBlockShape(f"{new.block_shape} is not stackable")

        new.parent = self
        new.next = self.next

        self.next = new

        new.check_toplevel()
        self.sprite.add_block(new)

        return new

    def duplicate_single_block(self) -> Block:
        return self.attach_block(self.dcopy())

    def attach_chain(self, *chain: Iterable[Block]) -> Block:
        attaching_block = self
        for _block in chain:
            attaching_block = attaching_block.attach_block(_block)

        return attaching_block

    def duplicate_chain(self) -> Block:
        return self.bottom_level_block.attach_chain(
            *map(Block.dcopy, self.attached_chain)
        )

    def slot_above(self, new: Block) -> Block:
        if not new.can_next:
            raise exceptions.BadBlockShape(f"{new.block_shape} cannot be stacked onto")

        elif self.block_shape.is_hat or not self.block_shape.is_stack:
            raise exceptions.BadBlockShape(f"{self.block_shape} is not stackable")

        new.parent, new.next = self.parent, self

        self.parent = new

        if new.parent:
            new.parent.next = new

        return self.sprite.add_block(new)

    def delete_single_block(self):
        if self.is_next_block:
            self.parent.next = self.next

        if self.next:
            self.next.parent = self.parent

            if self.is_top_level:
                self.next.is_top_level = True
                self.next.x, self.next.y = self.next.x, self.next.y

        self.sprite.remove_block(self)

    def delete_chain(self):
        for _block in self.attached_chain:
            _block.delete_single_block()

