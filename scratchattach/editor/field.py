from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import block, vlb

from . import base


class Field(base.BlockSubComponent):
    def __init__(self, _value: str | vlb.Variable | vlb.List | vlb.Broadcast, _id: str = None, *, _block: block.Block = None):
        """
        A field for a scratch block
        https://en.scratch-wiki.info/wiki/Scratch_File_Format#Blocks
        """
        self.value = _value
        self.id = _id
        """
        ID of associated VLB. Will be used to get VLB object during sprite initialisation, where it will be replaced with 'None'
        """
        super().__init__(_block)

    def __repr__(self):
        if self.id is not None:
            # This shouldn't occur after sprite initialisation
            return f"<Field {self.value!r} : {self.id!r}>"
        else:
            return f"<Field {self.value!r}>"

    @staticmethod
    def from_json(data: list[str, str | None]):
        # Sometimes you may have a stray field with no id. Not sure why
        while len(data) < 2:
            data.append(None)
        data = data[:2]

        _value, _id = data
        return Field(_value, _id)

    def to_json(self) -> dict:
        pass
