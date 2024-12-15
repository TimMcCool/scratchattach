"""
Collection of block information, stating input/field names and opcodes
New version of sbuild.py

May want to completely change this later
"""
from __future__ import annotations

from dataclasses import dataclass

from . import prim
from ..utils.enums import _EnumWrapper


@dataclass(init=True, repr=True)
class FieldUsage:
    name: str
    value_type: prim.PrimTypes = None


@dataclass(init=True, repr=True)
class SpecialFieldUsage(FieldUsage):
    name: str
    attrs: list[str] = None
    if attrs is None:
        attrs = []

    value_type: None = None


@dataclass(init=True, repr=True)
class InputUsage:
    name: str
    value_type: prim.PrimTypes = None
    default_obscurer: BlockUsage = None


@dataclass(init=True, repr=True)
class BlockUsage:
    opcode: str
    fields: list[FieldUsage] = None
    if fields is None:
        fields = []

    inputs: list[InputUsage] = None
    if inputs is None:
        inputs = []


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
