"""
Collection of block information, stating input/field names and opcodes
Not ready for use
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from . import prim
from scratchattach.utils.enums import _EnumWrapper


@dataclass
class FieldUsage:
    name: str
    value_type: Optional[prim.PrimTypes] = None


@dataclass
class SpecialFieldUsage(FieldUsage):
    name: str
    value_type: None = None # Order cannot be changed
    attrs: list[str] = field(default_factory=list)



@dataclass
class InputUsage:
    name: str
    value_type: Optional[prim.PrimTypes] = None
    default_obscurer: Optional[BlockUsage] = None


@dataclass
class BlockUsage:
    opcode: str
    fields: Optional[list[FieldUsage]] = None
    if fields is None:
        fields = []

    inputs: Optional[list[InputUsage]] = None
    if inputs is None:
        inputs = []


class BlockUsages(_EnumWrapper):
    # Special Enum blocks
    MATH_NUMBER = BlockUsage(
        "math_number",
        [SpecialFieldUsage("NUM", attrs=["name", "value"])]
    )
    MATH_POSITIVE_NUMBER = BlockUsage(
        "math_positive_number",
        [SpecialFieldUsage("NUM", attrs=["name", "value"])]
    )
    MATH_WHOLE_NUMBER = BlockUsage(
        "math_whole_number",
        [SpecialFieldUsage("NUM", attrs=["name", "value"])]
    )
    MATH_INTEGER = BlockUsage(
        "math_integer",
        [SpecialFieldUsage("NUM", attrs=["name", "value"])]
    )
    MATH_ANGLE = BlockUsage(
        "math_angle",
        [SpecialFieldUsage("NUM", attrs=["name", "value"])]
    )
    COLOUR_PICKER = BlockUsage(
        "colour_picker",
        [SpecialFieldUsage("COLOUR", attrs=["name", "value"])]
    )
    TEXT = BlockUsage(
        "text",
        [SpecialFieldUsage("TEXT", attrs=["name", "value"])]
    )
    EVENT_BROADCAST_MENU = BlockUsage(
        "event_broadcast_menu",
        [SpecialFieldUsage("BROADCAST_OPTION", attrs=["name", "id", "value", "variableType"])]
    )
    DATA_VARIABLE = BlockUsage(
        "data_variable",
        [SpecialFieldUsage("VARIABLE", attrs=["name", "id", "value", "variableType"])]
    )
    DATA_LISTCONTENTS = BlockUsage(
        "data_listcontents",
        [SpecialFieldUsage("LIST", attrs=["name", "id", "value", "variableType"])]
    )
