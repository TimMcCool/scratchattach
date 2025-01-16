from __future__ import annotations

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from . import project

from . import base


class Monitor(base.ProjectSubcomponent):
    def __init__(self, reporter: Optional[base.NamedIDComponent] = None,
                 mode: str = "default",
                 opcode: str = "data_variable",
                 params: Optional[dict] = None,
                 sprite_name: Optional[str] = None,
                 value=0,
                 width: int | float = 0,
                 height: int | float = 0,
                 x: int | float = 5,
                 y: int | float = 5,
                 visible: bool = False,
                 slider_min: int | float = 0,
                 slider_max: int | float = 100,
                 is_discrete: bool = True, *, reporter_id: Optional[str] = None, _project: Optional[project.Project] = None):
        """
        Represents a variable/list monitor
        https://en.scratch-wiki.info/wiki/Scratch_File_Format#Monitors
        """
        assert isinstance(reporter, base.SpriteSubComponent) or reporter is None

        self.reporter_id = reporter_id
        """
        ID referencing the VLB being referenced. Replaced with None during project instantiation, where the reporter attribute is updated
        """

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

        super().__init__(_project)

    def __repr__(self):
        return f"Monitor<{self.opcode}>"

    @property
    def id(self):
        if self.reporter is not None:
            return self.reporter.id
            # if isinstance(self.reporter, str):
            #     return self.reporter
            # else:
            #     return self.reporter.id
        else:
            return self.reporter_id

    @staticmethod
    def from_json(data: dict):
        _id = data["id"]
        # ^^ NEED TO FIND REPORTER OBJECT

        mode = data["mode"]

        opcode = data["opcode"]
        params: dict = data["params"]

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

        return Monitor(None, mode, opcode, params, sprite_name, value, width, height, x, y, visible, slider_min,
                       slider_max, is_discrete, reporter_id=_id)

    def to_json(self):
        _json = {
            "id": self.id,
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

    def link_using_project(self):
        assert self.project is not None

        if self.opcode in ("data_variable", "data_listcontents", "event_broadcast_menu"):
            new_vlb = self.project.find_vlb(self.reporter_id, "id")
            if new_vlb is not None:
                self.reporter = new_vlb
                self.reporter_id = None

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
