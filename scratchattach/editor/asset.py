from __future__ import annotations

from dataclasses import dataclass
from hashlib import md5

from . import base, project, commons, sprite


@dataclass(init=True)
class AssetFile:
    filename: str
    data: bytes

    def __repr__(self):
        return f"AssetFile(filename={self.filename!r})"


class Asset(base.SpriteSubComponent):
    def __init__(self,
                 name: str = "costume1",
                 file_name: str = "b7853f557e4426412e64bb3da6531a99.svg",
                 _sprite: sprite.Sprite = None):
        """
        Represents a generic asset. Can be a sound or an image.
        https://en.scratch-wiki.info/wiki/Scratch_File_Format#Assets
        """
        try:
            asset_id, data_format = file_name.split('.')
        except ValueError:
            raise ValueError(f"Invalid file name: {file_name}, # of '.' in {file_name} ({file_name.count('.')}) != 2; "
                             f"(too many/few values to unpack)")
        self.name = name

        self.id = asset_id
        self.data_format = data_format

        super().__init__(_sprite)

    def __repr__(self):
        return f"Asset<{self.file_name}>"

    @property
    def file_name(self):
        return f"{self.id}.{self.data_format}"

    @property
    def md5ext(self):
        return self.file_name

    @staticmethod
    def from_json(data: dict):
        _name = data.get("name")
        _file_name = data.get("md5ext")
        if _file_name is None:
            if "dataFormat" in data and "assetId" in data:
                _id = data["assetId"]
                _data_format = data["dataFormat"]
                _file_name = f"{_id}.{_data_format}"

        return Asset(_name, _file_name)

    def to_json(self) -> dict:
        return {
            "name": self.name,

            "assetId": self.id,
            "md5ext": self.file_name,
            "dataFormat": self.data_format,
        }

    """
    @staticmethod
    def from_file(fp: str, name: str = None):
        image_types = ("png", "jpg", "jpeg", "svg")
        sound_types = ("wav", "mp3")
        
        # Should save data as well so it can be uploaded to scratch if required (add to project asset data)
        ...
    """


class Costume(Asset):
    def __init__(self,
                 name: str = "Cat",
                 file_name: str = "b7853f557e4426412e64bb3da6531a99.svg",

                 bitmap_resolution=None,
                 rotation_center_x: int | float = 48,
                 rotation_center_y: int | float = 50,
                 _sprite: sprite.Sprite = None):
        """
        A costume. An asset with additional properties
        https://en.scratch-wiki.info/wiki/Scratch_File_Format#Costumes
        """
        super().__init__(name, file_name, _sprite)

        self.bitmap_resolution = bitmap_resolution
        self.rotation_center_x = rotation_center_x
        self.rotation_center_y = rotation_center_y

    @staticmethod
    def from_json(data):
        _asset_load = Asset.from_json(data)

        bitmap_resolution = data.get("bitmapResolution")

        rotation_center_x = data["rotationCenterX"]
        rotation_center_y = data["rotationCenterY"]
        return Costume(_asset_load.name, _asset_load.file_name,

                       bitmap_resolution, rotation_center_x, rotation_center_y)

    def to_json(self) -> dict:
        _json = super().to_json()
        _json.update({
            "bitmapResolution": self.bitmap_resolution,
            "rotationCenterX": self.rotation_center_x,
            "rotationCenterY": self.rotation_center_y
        })
        return _json


class Sound(Asset):
    def __init__(self,
                 name: str = "pop",
                 file_name: str = "83a9787d4cb6f3b7632b4ddfebf74367.wav",

                 rate: int = None,
                 sample_count: int = None,
                 _sprite: sprite.Sprite = None):
        """
        A sound. An asset with additional properties
        https://en.scratch-wiki.info/wiki/Scratch_File_Format#Sounds
        """
        super().__init__(name, file_name, _sprite)

        self.rate = rate
        self.sample_count = sample_count

    @staticmethod
    def from_json(data):
        _asset_load = Asset.from_json(data)

        rate = data.get("rate")
        sample_count = data.get("sampleCount")
        return Sound(_asset_load.name, _asset_load.file_name, rate, sample_count)

    def to_json(self) -> dict:
        _json = super().to_json()
        commons.noneless_update(_json, {
            "rate": self.rate,
            "sampleCount": self.sample_count
        })
        return _json
