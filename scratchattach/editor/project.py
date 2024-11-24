from __future__ import annotations

import json
import warnings
from io import BytesIO, TextIOWrapper
from typing import Any, Iterable
from zipfile import ZipFile

from . import base, meta, extension, monitor, sprite, asset
from ..utils import exceptions


class Project(base.JSONSerializable):
    def __init__(self, _name:str=None, _meta: meta.Meta = None, _extensions: Iterable[extension.Extension] = (),
                 _monitors: Iterable[monitor.Monitor] = (), _sprites: Iterable[sprite.Sprite] = (), *,
                 _asset_data: list[asset.AssetFile] = None):
        # Defaulting for list parameters
        if _meta is None:
            _meta = meta.Meta()
        if _asset_data is None:
            _asset_data = []

        self.name = _name

        self.meta = _meta
        self.extensions = _extensions
        self.monitors = _monitors
        self.sprites = _sprites

        self.asset_data = _asset_data

        # Link sprites
        _stage_count = 0

        for _sprite in self.sprites:
            if _sprite.is_stage:
                _stage_count += 1

            _sprite.project = self
            _sprite.link_prims()
            _sprite.link_blocks()

        if _stage_count != 1:
            raise exceptions.InvalidStageCount(f"Project {self}")

    def __repr__(self):
        _ret = "Project<"
        if self.name is not None:
            _ret += f"name={self.name}, "
        _ret += f"meta={self.meta}"
        _ret += '>'
        return _ret

    @property
    def stage(self) -> sprite.Sprite:
        for _sprite in self.sprites:
            if _sprite.is_stage:
                return _sprite

    def to_json(self) -> dict | list | Any:
        pass

    @staticmethod
    def from_json(data: dict | list | Any):
        assert isinstance(data, dict)

        # Load metadata
        _meta = meta.Meta.from_json(data.get("meta"))

        # Load extensions
        _extensions = []
        for _extension_data in data.get("extensions", []):
            _extensions.append(extension.Extension.from_json(_extension_data))

        # Load monitors
        _monitors = []
        for _monitor_data in data.get("monitors", []):
            _monitors.append(monitor.Monitor.from_json(_monitor_data))

        # Load sprites (targets)
        _sprites = []
        for _sprite_data in data.get("targets", []):
            _sprites.append(sprite.Sprite.from_json(_sprite_data))

        return Project(None, _meta, _extensions, _monitors, _sprites)

    @staticmethod
    def from_sb3(data: str | bytes | TextIOWrapper, load_assets: bool = True, _name: str = None):
        """
        Load a project from an .sb3 file/bytes/file path
        """

        if _name is None:
            if hasattr(data, "name"):
                _name = data.name

        if not isinstance(_name, str) and _name is not None:
            _name = str(_name)

        if isinstance(data, bytes):
            data = BytesIO(data)

        elif isinstance(data, str):
            if _name is None:
                _name = data.split('/')[-1]
                _name = '.'.join(_name.split('.')[:-1])

            data = open(data, "rb")
        with data:
            # For if the sb3 is just JSON (e.g. if it's exported from scratchattach)
            try:
                project = Project.from_json(json.load(data))
            except ValueError:
                with ZipFile(data) as archive:
                    data = json.loads(archive.read("project.json"))

                    project = Project.from_json(data)

                    # Also load assets
                    if load_assets:
                        asset_data = []
                        for filename in archive.namelist():
                            if filename != "project.json":
                                asset_data.append(
                                    asset.AssetFile(filename, archive.read(filename))
                                )
                        project.asset_data = asset_data
                    else:
                        warnings.warn(
                            "Loading sb3 without loading assets. When exporting the project, there may be errors due to assets not being uploaded to the Scratch website")

            project.name = _name
            return project
