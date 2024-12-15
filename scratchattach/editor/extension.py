from __future__ import annotations


from dataclasses import dataclass

from . import base
from ..utils import enums


@dataclass(init=True, repr=True)
class Extension(base.JSONSerializable):
    code: str
    name: str = None

    def __eq__(self, other):
        return self.code == other.code

    @staticmethod
    def from_json(data: str):
        assert isinstance(data, str)
        _extension = Extensions.find(data, "code")
        if _extension is None:
            _extension = Extension(data)

        return _extension

    def to_json(self) -> str:
        return self.code


class Extensions(enums._EnumWrapper):
    BOOST = Extension("boost", "LEGO BOOST Extension")
    EV3 = Extension("ev3", "LEGO MINDSTORMS EV3 Extension")
    GDXFOR = Extension("gdxfor", "Go Direct Force & Acceleration Extension")
    MAKEYMAKEY = Extension("makeymakey", "Makey Makey Extension")
    MICROBIT = Extension("microbit", "micro:bit Extension")
    MUSIC = Extension("music", "Music Extension")
    PEN = Extension("pen", "Pen Extension")
    TEXT2SPEECH = Extension("text2speech", "Text to Speech Extension")
    TRANSLATE = Extension("translate", "Translate Extension")
    VIDEOSENSING = Extension("videoSensing", "Video Sensing Extension")
    WEDO2 = Extension("wedo2", "LEGO Education WeDo 2.0 Extension")
    COREEXAMPLE = Extension("coreExample", "CoreEx Extension")
