from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import md5, sha256
import requests

from . import base, commons, sprite, build_defaulting
from typing import Optional


@dataclass(init=True, repr=True)
class AssetFile:
    """
    Represents the file information for an asset (not the asset metdata)
    - stores the filename, data, and md5 hash
    """
    filename: str
    _data: Optional[bytes] = field(repr=False, default=None)
    _md5: str = field(repr=False, default_factory=str)

    @property
    def data(self) -> bytes:
        """
        Return the contents of the asset file, as bytes
        """
        if self._data is None:
            # Download and cache
            rq = requests.get(f"https://assets.scratch.mit.edu/internalapi/asset/{self.filename}/get/")
            # print(f"Downloaded {url}")
            if rq.status_code != 200:
                raise ValueError(f"Can't download asset {self.filename}\nIs not uploaded to scratch! Response: {rq.text}")

            self._data = rq.content

        return self._data

    @data.setter
    def data(self, data: bytes):
        self._data = data

    @property
    def md5(self) -> str:
        """
        Compute/retrieve the md5 hex-digest of the asset file data
        """
        if self._md5 is None:
            self._md5 = md5(self.data).hexdigest()

        return self._md5

    @property
    def sha256(self) -> str:
        return sha256(self.data).hexdigest()

class Asset(base.SpriteSubComponent):
    def __init__(self,
                 name: str = "costume1",
                 file_name: str = "b7853f557e4426412e64bb3da6531a99.svg",
                 _sprite: commons.SpriteInput = build_defaulting.SPRITE_DEFAULT):
        """
        Represents a generic asset, with metadata. Can be a sound or a costume.
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
        return f"Asset<{self.name!r}>"

    @property
    def folder(self):
        """
        Get the folder name of this asset, based on the asset name. Uses the TurboWarp syntax
        """
        return commons.get_folder_name(self.name)

    @property
    def name_nfldr(self):
        """
        Get the asset name after removing the folder name. Uses the TurboWarp syntax
        """
        return commons.get_name_nofldr(self.name)

    @property
    def file_name(self):
        """
        Get the exact file name, as it would be within an sb3 file
        equivalent to the md5ext value using in scratch project JSON
        """
        return f"{self.id}.{self.data_format}"

    @property
    def md5ext(self):
        """
        Get the exact file name, as it would be within an sb3 file
        equivalent to the md5ext value using in scratch project JSON

        (alias for file_name)
        """
        return self.file_name

    @property
    def parent(self):
        """
        Return the project (body) that this asset is attached to. If there is no attached project,
        try returning the attached sprite instead.
        """
        if self.project is None:
            return self.sprite
        else:
            return self.project

    @property
    def asset_file(self) -> AssetFile:
        """
        Get the associated asset file object for this asset object
        """
        for asset_file in self.parent.asset_data:
            if asset_file.filename == self.file_name:
                return asset_file

        # No pre-existing asset file object; create one and add it to the project
        asset_file = AssetFile(self.file_name)
        self.project.asset_data.append(asset_file)
        return asset_file

    @staticmethod
    def from_json(data: dict):
        """
        Load asset data from project.json
        """
        _name = data.get("name")
        assert isinstance(_name, str)
        _file_name = data.get("md5ext")
        if _file_name is None:
            if "dataFormat" in data and "assetId" in data:
                _id = data["assetId"]
                _data_format = data["dataFormat"]
                _file_name = f"{_id}.{_data_format}"
            else:
                _file_name = ""
        assert isinstance(_file_name, str)

        return Asset(_name, _file_name)

    def to_json(self) -> dict:
        """
        Convert asset data to project.json format
        """
        return {
            "name": self.name,

            "assetId": self.id,
            "md5ext": self.file_name,
            "dataFormat": self.data_format,
        }

    # todo: implement below:
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
                 _sprite: commons.SpriteInput = build_defaulting.SPRITE_DEFAULT):
        """
        A costume (image). An asset with additional properties
        https://en.scratch-wiki.info/wiki/Scratch_File_Format#Costumes
        """
        super().__init__(name, file_name, _sprite)

        self.bitmap_resolution = bitmap_resolution
        self.rotation_center_x = rotation_center_x
        self.rotation_center_y = rotation_center_y

    @staticmethod
    def from_json(data):
        """
        Load costume data from project.json
        """
        _asset_load = Asset.from_json(data)

        bitmap_resolution = data.get("bitmapResolution")

        rotation_center_x = data.get("rotationCenterX", 0)
        rotation_center_y = data.get("rotationCenterY", 0)
        return Costume(_asset_load.name, _asset_load.file_name,

                       bitmap_resolution, rotation_center_x, rotation_center_y)

    def to_json(self) -> dict:
        """
        Convert costume to project.json format
        """
        _json = super().to_json()
        _json.update({
            "rotationCenterX": self.rotation_center_x,
            "rotationCenterY": self.rotation_center_y
        })
        if self.bitmap_resolution is not None:
            _json["bitmapResolution"] = self.bitmap_resolution

        return _json


class Sound(Asset):
    def __init__(self,
                 name: str = "pop",
                 file_name: str = "83a9787d4cb6f3b7632b4ddfebf74367.wav",

                 rate: Optional[int] = None,
                 sample_count: Optional[int] = None,
                 _sprite: sprite.Sprite = build_defaulting.SPRITE_DEFAULT):
        """
        A sound. An asset with additional properties
        https://en.scratch-wiki.info/wiki/Scratch_File_Format#Sounds
        """
        super().__init__(name, file_name, _sprite)

        self.rate = rate
        self.sample_count = sample_count

    @staticmethod
    def from_json(data):
        """
        Load sound from project.json
        """
        _asset_load = Asset.from_json(data)

        rate = data.get("rate")
        sample_count = data.get("sampleCount")
        return Sound(_asset_load.name, _asset_load.file_name, rate, sample_count)

    def to_json(self) -> dict:
        """
        Convert Sound to project.json format
        """
        _json = super().to_json()
        commons.noneless_update(_json, {
            "rate": self.rate,
            "sampleCount": self.sample_count
        })
        return _json
