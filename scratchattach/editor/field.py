from __future__ import annotations

from typing import Optional, TYPE_CHECKING, Final


if TYPE_CHECKING:
    from . import block, vlb

from . import base, commons


class Types:
    VARIABLE: Final[str] = "variable"
    LIST: Final[str] = "list"
    BROADCAST: Final[str] = "broadcast"
    DEFAULT: Final[str] = "default"


class Field(base.BlockSubComponent):
    def __init__(self, _value: str | vlb.Variable | vlb.List | vlb.Broadcast, _id: Optional[str] = None, *, _block: Optional[block.Block] = None):
        """
        A field for a scratch block
        https://en.scratch-wiki.info/wiki/Scratch_File_Format#Blocks:~:text=it.%5B9%5D-,fields,element%2C%20which%20is%20the%20ID%20of%20the%20field%27s%20value.%5B10%5D,-shadow
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

    @property
    def value_id(self):
        if self.id is not None:
            return self.id
        else:
            if hasattr(self.value, "id"):
                return self.value.id
            else:
                return None

    @property
    def value_str(self):
        if not isinstance(self.value, base.NamedIDComponent):
            return self.value
        else:
            return self.value.name

    @property
    def name(self) -> str:
        for _name, _field in self.block.fields.items():
            if _field is self:
                return _name

    @property
    def type(self):
        """
        Infer the type of value that this field holds
        :return: A string (from field.Types) as a name of the type
        """
        if "variable" in self.name.lower():
            return Types.VARIABLE
        elif "list" in self.name.lower():
            return Types.LIST
        elif "broadcast" in self.name.lower():
            return Types.BROADCAST
        else:
            return Types.DEFAULT

    @staticmethod
    def from_json(data: list[str, str | None]):
        # Sometimes you may have a stray field with no id. Not sure why
        while len(data) < 2:
            data.append(None)
        data = data[:2]

        _value, _id = data
        return Field(_value, _id)

    def to_json(self) -> dict:
        return commons.trim_final_nones([
            self.value_str, self.value_id
        ])
