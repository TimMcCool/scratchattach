from __future__ import annotations

import json
import os
import warnings
from io import BytesIO, TextIOWrapper
from typing import Optional, Iterable, Generator, BinaryIO
from zipfile import ZipFile

from . import base, meta, extension, monitor, sprite, asset, vlb, twconfig, comment, commons
from ..site import session
from ..site.project import get_project
from ..utils import exceptions


class Project(base.JSONExtractable):
    def __init__(self, _name: Optional[str] = None, _meta: Optional[meta.Meta] = None, _extensions: Iterable[extension.Extension] = (),
                 _monitors: Iterable[monitor.Monitor] = (), _sprites: Iterable[sprite.Sprite] = (), *,
                 _asset_data: Optional[list[asset.AssetFile]] = None, _session: Optional[session.Session] = None):
        # Defaulting for list parameters
        if _meta is None:
            _meta = meta.Meta()
        if _asset_data is None:
            _asset_data = []

        self._session = _session

        self.name = _name

        self.meta = _meta
        self.extensions = _extensions
        self.monitors = list(_monitors)
        self.sprites = list(_sprites)

        self.asset_data = _asset_data

        self._tw_config_comment = None

        # Link subcomponents
        for iterable in (self.monitors, self.sprites):
            for _subcomponent in iterable:
                _subcomponent.project = self

        # Link sprites
        _stage_count = 0

        for _sprite in self.sprites:
            if _sprite.is_stage:
                _stage_count += 1

            _sprite.link_subcomponents()

        # Link monitors
        for _monitor in self.monitors:
            _monitor.link_using_project()

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
        warnings.warn(f"Could not find stage for {self.name}")

    def to_json(self) -> dict:
        _json = {
            "targets": [_sprite.to_json() for _sprite in self.sprites],
            "monitors": [_monitor.to_json() for _monitor in self.monitors],
            "extensions": [_extension.to_json() for _extension in self.extensions],
            "meta": self.meta.to_json(),
        }

        return _json

    @property
    def assets(self) -> Generator[asset.Asset, None, None]:
        for _sprite in self.sprites:
            for _asset in _sprite.assets:
                yield _asset

    @property
    def tw_config_comment(self) -> comment.Comment | None:
        for _comment in self.stage.comments:
            if twconfig.is_valid_twconfig(_comment.text):
                return _comment
        return None

    @property
    def tw_config(self) -> twconfig.TWConfig | None:
        _comment = self.tw_config_comment
        if _comment:
            return twconfig.TWConfig.from_str(_comment.text)
        return None

    @property
    def all_ids(self):
        _ret = []
        for _sprite in self.sprites:
            _ret += _sprite.all_ids
        return _ret

    @property
    def new_id(self):
        return commons.gen_id()

    @staticmethod
    def from_json(data: dict):
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
    def load_json(data: str | bytes | TextIOWrapper | BinaryIO, load_assets: bool = True, _name: Optional[str] = None):
        """
        Load project JSON and assets from an .sb3 file/bytes/file path
        :return: Project name, asset data, json string
        """
        _dir_for_name = None

        if _name is None:
            if hasattr(data, "name"):
                _dir_for_name = data.name

        if not isinstance(_name, str) and _name is not None:
            _name = str(_name)

        if isinstance(data, bytes):
            data = BytesIO(data)

        elif isinstance(data, str):
            _dir_for_name = data
            data = open(data, "rb")

        if _name is None and _dir_for_name is not None:
            # Remove any directory names and the file extension
            _name = _dir_for_name.split('/')[-1]
            _name = '.'.join(_name.split('.')[:-1])

        asset_data = []
        with data:
            # For if the sb3 is just JSON (e.g. if it's exported from scratchattach)
            if commons.is_valid_json(data):
                json_str = data

            else:
                with ZipFile(data) as archive:
                    json_str = archive.read("project.json")

                    # Also load assets
                    if load_assets:
                        for filename in archive.namelist():
                            if filename != "project.json":
                                md5_hash = filename.split('.')[0]

                                asset_data.append(
                                    asset.AssetFile(filename, archive.read(filename), md5_hash)
                                )

                    else:
                        warnings.warn(
                            "Loading sb3 without loading assets. When exporting the project, there may be errors due to assets not being uploaded to the Scratch website")

            return _name, asset_data, json_str

    @classmethod
    def from_sb3(cls, data: str | bytes | TextIOWrapper | BinaryIO, load_assets: bool = True, _name: Optional[str] = None):
        """
        Load a project from an .sb3 file/bytes/file path
        """
        _name, asset_data, json_str = cls.load_json(data, load_assets, _name)
        data = json.loads(json_str)

        project = cls.from_json(data)
        project.name = _name
        project.asset_data = asset_data

        return project

    @staticmethod
    def from_id(project_id: int, _name: Optional[str] = None):
        _proj = get_project(project_id)
        data = json.loads(_proj.get_json())

        if _name is None:
            _name = _proj.title
        _name = str(_name)

        _proj = Project.from_json(data)
        _proj.name = _name
        return _proj

    def find_vlb(self, value: str | None, by: str = "name",
                 multiple: bool = False) -> vlb.Variable | vlb.List | vlb.Broadcast | list[
        vlb.Variable | vlb.List | vlb.Broadcast]:
        _ret = []
        for _sprite in self.sprites:
            val = _sprite.find_vlb(value, by, multiple)
            if multiple:
                _ret += val
            else:
                if val is not None:
                    return val
        if multiple:
            return _ret

    def find_sprite(self, value: str | None, by: str = "name",
                 multiple: bool = False) -> sprite.Sprite | list[sprite.Sprite]:
        _ret = []
        for _sprite in self.sprites:
            if by == "name":
                _val = _sprite.name
            else:
                _val = getattr(_sprite, by)

            if _val == value:
                if multiple:
                    _ret.append(_sprite)
                else:
                    return _sprite

        if multiple:
            return _ret

    def export(self, fp: str, *, auto_open: bool = False, export_as_zip: bool = True):
        data = self.to_json()

        if export_as_zip:
            with ZipFile(fp, "w") as archive:
                for _asset in self.assets:
                    asset_file = _asset.asset_file
                    if asset_file.filename not in archive.namelist():
                        archive.writestr(asset_file.filename, asset_file.data)

                archive.writestr("project.json", json.dumps(data))
        else:
            with open(fp, "w") as json_file:
                json.dump(data, json_file)

        if auto_open:
            os.system(f"explorer.exe \"{fp}\"")

    def add_monitor(self, _monitor: monitor.Monitor) -> monitor.Monitor:
        _monitor.project = self
        _monitor.reporter_id = self.new_id
        self.monitors.append(_monitor)
