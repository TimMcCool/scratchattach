from __future__ import annotations

from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from . import block

from . import base, commons, prim
from dataclasses import dataclass


@dataclass(init=True)
class ShadowStatus:
    idx: int
    name: str

    def __repr__(self):
        return f"<ShadowStatus {self.name!r} ({self.idx})>"


class ShadowStatuses:
    # Not an enum so you don't need to do .value
    HAS_SHADOW: Final[ShadowStatus] = ShadowStatus(1, "has shadow")
    NO_SHADOW: Final[ShadowStatus] = ShadowStatus(2, "no shadow")
    OBSCURED: Final[ShadowStatus] = ShadowStatus(3, "obscured")

    @classmethod
    def find(cls, idx: int) -> ShadowStatus:
        for status in (cls.HAS_SHADOW, cls.NO_SHADOW, cls.OBSCURED):
            if status.idx == idx:
                return status

        if not 1 <= idx <= 3:
            raise ValueError(f"Invalid ShadowStatus idx={idx}")


class Input(base.BlockSubComponent):
    def __init__(self, _shadow: ShadowStatus = ShadowStatuses.HAS_SHADOW, _value: prim.Prim = None, _id: str = None,
                 _obscurer: block.Block = None, *, _obscurer_id: str = None, _block: block.Block = None):
        """
        An input for a scratch block
        https://en.scratch-wiki.info/wiki/Scratch_File_Format#Blocks:~:text=inputs,it.%5B9%5D
        """
        super().__init__(_block)

        self.shadow = _shadow
        self.value = _value
        self.obscurer = _obscurer

        self._id = _id
        """
        ID referring to the input value. Upon project initialisation, this will be set to None and the value attribute will be set to the relevant object
        """
        self._obscurer_id = _obscurer_id
        """
        ID referring to the obscurer. Upon project initialisation, this will be set to None and the obscurer attribute will be set to the relevant block
        """

    def __repr__(self):
        if self._id is not None:
            return f"<Input<id={self._id!r}>"
        else:
            return f"<Input {self.value!r}>"

    @staticmethod
    def from_json(data: list):
        _shadow = ShadowStatuses.find(data[0])

        _value, _id = None, None
        if isinstance(data[1], list):
            _value = prim.Prim.from_json(data[1])
        else:
            _id = data[1]

        _obscurer_id = commons.safe_get(data, 2)
        return Input(_shadow, _value, _id, _obscurer_id)

    def to_json(self) -> list:
        pass

    def link_using_block(self):
        if self._id is not None:
            new_value = self.sprite.find_block(self._id, "id")
            if new_value is not None:
                self.value = new_value
                self._id = None

        if self._obscurer_id is not None:
            new_block = self.sprite.find_block(self._obscurer_id, "id")
            if new_block is not None:
                self.obscurer = new_block
                self._obscurer_id = None

        if isinstance(self.value, prim.Prim):
            self.value.sprite = self.sprite
            self.value.link_using_sprite()
