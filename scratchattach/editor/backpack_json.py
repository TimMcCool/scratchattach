"""
Module to deal with the backpack's weird JSON format, by overriding with new load methods
"""
from __future__ import annotations

from . import block, prim, field, inputs, mutation, sprite


def parse_prim_fields(_fields: dict[str]) -> tuple[str | None, str | None, str | None]:
    """
    Function for reading the fields in a backpack **primitive**
    """
    for key, value in _fields.items():
        key: str
        value: dict[str, str]
        prim_value, prim_name, prim_id = (None,) * 3
        if key == "NUM":
            prim_value = value.get("value")
        else:
            prim_name = value.get("value")
            prim_id = value.get("id")

        # There really should only be 1 item, and this function can only return for that item
        return prim_value, prim_name, prim_id
    return (None,) * 3


class BpField(field.Field):
    """
    A normal field but with a different load method
    """

    @staticmethod
    def from_json(data: dict[str, str]) -> field.Field:
        # We can very simply convert it to the regular format
        data = [data.get("value"), data.get("id")]
        return field.Field.from_json(data)


class BpInput(inputs.Input):
    """
    A normal input but with a different load method
    """

    @staticmethod
    def from_json(data: dict[str, str]) -> inputs.Input:
        # The actual data is stored in a separate prim block
        _id = data.get("shadow")
        _obscurer_id = data.get("block")

        if _obscurer_id == _id:
            # If both the shadow and obscurer are the same, then there is no actual obscurer
            _obscurer_id = None
        # We cannot work out the shadow status yet since that is located in the primitive
        return inputs.Input(None, _id=_id, _obscurer_id=_obscurer_id)


class BpBlock(block.Block):
    """
    A normal block but with a different load method
    """

    @staticmethod
    def from_json(data: dict) -> prim.Prim | block.Block:
        """
        Load a block in the **backpack** JSON format
        :param data: A dictionary (not list)
        :return: A new block/prim object
        """
        _opcode = data["opcode"]

        _x, _y = data.get("x"), data.get("y")
        if prim.is_prim_opcode(_opcode):
            # This is actually a prim
            prim_value, prim_name, prim_id = parse_prim_fields(data["fields"])
            return prim.Prim(prim.PrimTypes.find(_opcode, "opcode"),
                             prim_value, prim_name, prim_id)

        _next_id = data.get("next")
        _parent_id = data.get("parent")

        _shadow = data.get("shadow", False)
        _top_level = data.get("topLevel", _parent_id is None)

        _inputs = {}
        for _input_code, _input_data in data.get("inputs", {}).items():
            _inputs[_input_code] = BpInput.from_json(_input_data)

        _fields = {}
        for _field_code, _field_data in data.get("fields", {}).items():
            _fields[_field_code] = BpField.from_json(_field_data)

        if "mutation" in data:
            _mutation = mutation.Mutation.from_json(data["mutation"])
        else:
            _mutation = None

        return block.Block(_opcode, _shadow, _top_level, _mutation, _fields, _inputs, _x, _y, _next_id=_next_id,
                           _parent_id=_parent_id)


def load_script(_script_data: list[dict]) -> sprite.Sprite:
    """
    Loads a script into a sprite from the backpack JSON format
    :param _script_data: Backpack script JSON data
    :return: a blockchain object containing the script
    """
    # Using a sprite since it simplifies things, e.g. local global loading
    _blockchain = sprite.Sprite()

    for _block_data in _script_data:
        _block = BpBlock.from_json(_block_data)
        _block.sprite = _blockchain
        _blockchain.blocks[_block_data["id"]] = _block

    _blockchain.link_subcomponents()
    return _blockchain
