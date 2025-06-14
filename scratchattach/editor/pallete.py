"""
Collection of block information, stating input/field names and opcodes
New version of sbuild.py

May want to completely change this later
"""
from __future__ import annotations

from dataclasses import dataclass, field, InitVar

from scratchattach.editor import prim
from scratchattach.utils.enums import _EnumWrapper


@dataclass
class FieldUsage:
    name: str
    value_type: prim.PrimTypes | None = None


@dataclass
class SpecialFieldUsage(FieldUsage):
    name: InitVar[str]
    attrs: list[str] = field(default_factory=list)
    value_type: InitVar[None]

    def __post_init__(self, name: str, value_type: None = None):
        super().__init__(name, value_type)


@dataclass
class InputUsage:
    name: str
    value_type: prim.PrimTypes | None = None
    default_obscurer: BlockUsage | None = None


@dataclass
class BlockUsage:
    opcode: str
    fields: list[FieldUsage] = field(default_factory=list)
    inputs: list[InputUsage] = field(default_factory=list)

class BlockUsages(_EnumWrapper):
    # Special Enum blocks
    MATH_NUMBER = BlockUsage(
        "math_number",
        [SpecialFieldUsage("NUM", ["name", "value"])]
    )
    MATH_POSITIVE_NUMBER = BlockUsage(
        "math_positive_number",
        [SpecialFieldUsage("NUM", ["name", "value"])]
    )
    MATH_WHOLE_NUMBER = BlockUsage(
        "math_whole_number",
        [SpecialFieldUsage("NUM", ["name", "value"])]
    )
    MATH_INTEGER = BlockUsage(
        "math_integer",
        [SpecialFieldUsage("NUM", ["name", "value"])]
    )
    MATH_ANGLE = BlockUsage(
        "math_angle",
        [SpecialFieldUsage("NUM", ["name", "value"])]
    )
    COLOUR_PICKER = BlockUsage(
        "colour_picker",
        [SpecialFieldUsage("COLOUR", ["name", "value"])]
    )
    TEXT = BlockUsage(
        "text",
        [SpecialFieldUsage("TEXT", ["name", "value"])]
    )
    EVENT_BROADCAST_MENU = BlockUsage(
        "event_broadcast_menu",
        [SpecialFieldUsage("BROADCAST_OPTION", ["name", "id", "value", "variableType"])]
    )
    DATA_VARIABLE = BlockUsage(
        "data_variable",
        [SpecialFieldUsage("VARIABLE", ["name", "id", "value", "variableType"])]
    )
    DATA_LISTCONTENTS = BlockUsage(
        "data_listcontents",
        [SpecialFieldUsage("LIST", ["name", "id", "value", "variableType"])]
    )
