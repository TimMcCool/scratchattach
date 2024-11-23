from typing import Any

from . import base


class Monitor(base.ProjectPart):
    def __init__(self, reporter: base.SpriteSubComponent = None,
                 mode: str = "default",
                 opcode: str = "data_variable",
                 params: dict = None,
                 sprite_name: str = None,
                 value=0,
                 width: int | float = 0,
                 height: int | float = 0,
                 x: int | float = 5,
                 y: int | float = 5,
                 visible: bool = False,
                 slider_min: int | float = 0,
                 slider_max: int | float = 100,
                 is_discrete: bool = True):
        """
        Represents a variable/list monitor
        https://en.scratch-wiki.info/wiki/Scratch_File_Format#Monitors
        """
        assert isinstance(reporter, base.SpriteSubComponent)

        self.reporter = reporter
        if params is None:
            params = {}

        self.mode = mode

        self.opcode = opcode
        self.params = params

        self.sprite_name = sprite_name

        self.value = value

        self.width, self.height = width, height
        self.x, self.y = x, y

        self.visible = visible

        self.slider_min, self.slider_max = slider_min, slider_max
        self.is_discrete = is_discrete

    def __repr__(self):
        return f"Monitor<{self.opcode}>"

    @staticmethod
    def from_json(data: dict | list | Any):
        _id = data["id"]
        mode = data["mode"]

        opcode = data["opcode"]
        params = data["params"]

        sprite_name = data["spriteName"]

        value = data["value"]

        width, height = data["width"], data["height"]
        x, y = data["x"], data["y"]

        visible = data["visible"]

        if "isDiscrete" in data.keys():
            slider_min, slider_max = data["sliderMin"], data["sliderMax"]
            is_discrete = data["isDiscrete"]
        else:
            slider_min, slider_max, is_discrete = None, None, None

        return Monitor(_id, mode, opcode, params, sprite_name, value, width, height, x, y, visible, slider_min,
                       slider_max, is_discrete)

    def to_json(self):
        _json = {
            "id": f"PLEASE GET ID FROM VALUE {self.reporter}",
            "mode": self.mode,

            "opcode": self.opcode,
            "params": self.params,

            "spriteName": self.sprite_name,

            "value": self.value,

            "width": self.width,
            "height": self.height,

            "x": self.x,
            "y": self.y,

            "visible": self.visible
        }
        if self.is_discrete is not None:
            _json["sliderMin"] = self.slider_min
            _json["sliderMax"] = self.slider_max
            _json["isDiscrete"] = self.is_discrete

        return _json

    # @staticmethod
    # def from_reporter(reporter: Block, _id: str = None, mode: str = "default",
    #                   opcode: str = None, sprite_name: str = None, value=0, width: int | float = 0,
    #                   height: int | float = 0,
    #                   x: int | float = 5, y: int | float = 5, visible: bool = False, slider_min: int | float = 0,
    #                   slider_max: int | float = 100, is_discrete: bool = True, params: dict = None):
    #     if "reporter" not in reporter.stack_type:
    #         warnings.warn(f"{reporter} is not a reporter block; the monitor will return '0'")
    #     elif "(menu)" in reporter.stack_type:
    #         warnings.warn(f"{reporter} is a menu block; the monitor will return '0'")
    #     # Maybe add note that length of list doesn't work fsr?? idk
    #     if _id is None:
    #         _id = reporter.opcode
    #     if opcode is None:
    #         opcode = reporter.opcode  # .replace('_', ' ')

    #     if params is None:
    #         params = {}
    #     for field in reporter.fields:
    #         if field.value_id is None:
    #             params[field.id] = field.value
    #         else:
    #             params[field.id] = field.value, field.value_id

    #     return Monitor(
    #         _id,
    #         mode,
    #         opcode,

    #         params,
    #         sprite_name,
    #         value,

    #         width, height,
    #         x, y,
    #         visible,
    #         slider_min, slider_max, is_discrete
    #     )
