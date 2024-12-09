"""
Parser for TurboWarp settings configuration
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from typing import Any

from . import commons, base

_START = """Configuration for https://turbowarp.org/
You can move, resize, and minimize this comment, but don't edit it by hand. This comment can be deleted to remove the stored settings.
"""
_END = " // _twconfig_"


@dataclass(init=True, repr=True)
class TWConfig(base.JSONSerializable):
    framerate: int = None,
    interpolation: bool = False,
    hq_pen: bool = False,
    max_clones: float | int | None = None,
    misc_limits: bool = True,
    fencing: bool = True
    width: int = None
    height: int = None

    @staticmethod
    def from_json(data: dict) -> TWConfig:
        # Non-runtime options
        _framerate = data.get("framerate")
        _interpolation = data.get("interpolation", False)
        _hq_pen = data.get("hq", False)

        # Runtime options
        _runtime_options = data.get("runtimeOptions", {})

        # Luckily for us, the JSON module actually accepts the 'Infinity' literal. Otherwise, it would be a right pain
        _max_clones = _runtime_options.get("maxClones")
        _misc_limits = _runtime_options.get("miscLimits", True)
        _fencing = _runtime_options.get("fencing", True)

        # Custom stage size
        _width = data.get("width")
        _height = data.get("height")

        return TWConfig(_framerate, _interpolation, _hq_pen, _max_clones, _misc_limits, _fencing, _width, _height)

    def to_json(self) -> dict:
        runtime_options = {}
        commons.noneless_update(
            runtime_options,
            {
                "maxClones": self.max_clones,
                "miscLimits": none_if_eq(self.misc_limits, True),
                "fencing": none_if_eq(self.fencing, True)
            })

        data = {}
        commons.noneless_update(data, {
            "framerate": self.framerate,
            "runtimeOptions": runtime_options,
            "interpolation": none_if_eq(self.interpolation, False),
            "hq": none_if_eq(self.hq_pen, False),
            "width": self.width,
            "height": self.height
        })
        return data

    @property
    def infinite_clones(self):
        return self.max_clones == math.inf

    @staticmethod
    def from_str(string: str):
        return TWConfig.from_json(get_twconfig_data(string))


def is_valid_twconfig(string: str) -> bool:
    """
    Checks if some text is TWConfig (does not check the JSON itself)
    :param string: text (from a comment)
    :return: Boolean whether it is TWConfig
    """

    if string.startswith(_START) and string.endswith(_END):
        json_part = string[len(_START):-len(_END)]
        if commons.is_valid_json(json_part):
            return True
    return False


def get_twconfig_data(string: str) -> dict | None:
    try:
        return json.loads(string[len(_START):-len(_END)])
    except ValueError:
        return None


def none_if_eq(data, compare) -> Any | None:
    """
    Returns None if data and compare are the same
    :param data: Original data
    :param compare: Data to compare
    :return: Either the original data or None
    """
    if data == compare:
        return None
    else:
        return data
