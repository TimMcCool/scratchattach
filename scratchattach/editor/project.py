from __future__ import annotations

import json
import os
import string
import warnings
from io import BytesIO, TextIOWrapper
from typing import Optional, Iterable, Generator, BinaryIO
from typing_extensions import deprecated
from zipfile import ZipFile

from . import base, meta, extension, monitor, sprite, asset, vlb, twconfig, comment, commons, mutation
from scratchattach.site import session
from scratchattach.utils import exceptions


class Project(base.JSONExtractable):
    """
    A Project (body). Represents the editor contents of a scratch project
    """
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
        self.extensions: list[extension.Extension] = list(_extensions)
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
    def stage(self) -> Optional[sprite.Sprite]:
        for _sprite in self.sprites:
            if _sprite.is_stage:
                return _sprite
        warnings.warn(f"Could not find stage for {self.name}")
        return None

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
    @deprecated("Use get_project(id).body() instead")
    def from_id(project_id: int, _name: Optional[str] = None):
        raise Exception("This method is deprecated")
        # _proj = get_project(project_id)
        # data = json.loads(_proj.get_json())

        # if _name is None:
        #     _name = _proj.title
        # _name = str(_name)

        # _proj = Project.from_json(data)
        # _proj.name = _name
        # return _proj

    def find_vlb(self, value: str | None, by: str = "name",
                 multiple: bool = False) -> Optional[vlb.Variable | vlb.List | vlb.Broadcast | list[
        vlb.Variable | vlb.List | vlb.Broadcast]]:

        _ret: list[vlb.Variable | vlb.List | vlb.Broadcast] = []
        for _sprite in self.sprites:
            val = _sprite.find_vlb(value, by, multiple)
            if multiple:
                _ret += val
            else:
                if val is not None:
                    return val

        if multiple:
            return _ret

        return None

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
        """
        Bind a monitor to this project. Doing these manually can lead to interesting results.
        """
        _monitor.project = self
        _monitor.reporter_id = self.new_id
        self.monitors.append(_monitor)
        return _monitor

    def obfuscate(self, *, goto_origin: bool=True) -> None:
        """
        Randomly set all the variable names etc. Do not upload this project to the scratch website, as it is
        against the community guidelines.
        """
        # this code is an embarrassing mess. If certain features are added to sa.editor, then it could become a lot cleaner
        chars = string.ascii_letters + string.digits + string.punctuation

        def b10_to_cbase(b10: int | float):
            ret = ''
            new_base = len(chars)
            while b10 >= 1:
                ret = chars[int(b10 % new_base)] + ret
                b10 /= new_base

            return ret

        used = 0

        def rand():
            nonlocal used
            used += 1

            return b10_to_cbase(used)

        for _sprite in self.sprites:
            procedure_mappings: dict[str, str] = {}
            argument_mappings: dict[str, str] = {}
            done_args: list[mutation.Argument] = []

            for _variable in _sprite.variables:
                _variable.name = rand()
            for _list in _sprite.lists:
                _list.name = rand()
            # don't rename broadcasts as these can be dynamically called

            def arg_get(name: str) -> str:
                if name not in argument_mappings:
                    argument_mappings[name] = rand()
                return argument_mappings[name]

            for _block in _sprite.blocks.values():
                if goto_origin:
                    _block.x, _block.y = 0, 0

                # TODO: Add special handling for turbowarp debugger blocks
                if _block.opcode in ("procedures_call", "procedures_prototype", "procedures_definition"):
                    if _block.mutation is None:
                        continue

                    proccode = _block.mutation.proc_code
                    if proccode is None:
                        continue

                    if proccode not in procedure_mappings:
                        parsed_ppc = _block.mutation.parsed_proc_code

                        if parsed_ppc is None:
                            continue

                        new: list[str | mutation.ArgumentType] = []
                        for item in parsed_ppc:
                            if isinstance(item, str):
                                item = rand()

                            new.append(item)

                        new_proccode = mutation.construct_proccode(*new)
                        procedure_mappings[proccode] = new_proccode

                    _block.mutation.proc_code = procedure_mappings[proccode]

                    assert _block.mutation.arguments is not None
                    for arg in _block.mutation.arguments:
                        if arg in done_args:
                            continue
                        done_args.append(arg)

                        arg.name = arg_get(arg.name)

                    # print(_block, _block.mutation)
                elif _block.opcode in ("argument_reporter_string_number", "argument_reporter_boolean"):
                    arg_name = _block.fields["VALUE"].value
                    assert isinstance(arg_name, str)
                    _block.fields["VALUE"].value = arg_get(arg_name)


                # print(argument_mappings)

            if goto_origin:
                for _comment in _sprite.comments:
                    _comment.x, _comment.y = 0, 0
