from __future__ import annotations

import warnings
from typing import Any

from . import base, project, vlb, asset, comment, prim, block
from ..utils import exceptions


class Sprite(base.ProjectSubcomponent):
    def __init__(self, is_stage: bool = False, name: str = '', _current_costume: int = 1, _layer_order: int = None,
                 _volume: int = 100,
                 _broadcasts: list[vlb.Broadcast] = None,
                 _variables: list[vlb.Variable] = None, _lists: list[vlb.List] = None,
                 _costumes: list[asset.Costume] = None, _sounds: list[asset.Sound] = None,
                 _comments: list[comment.Comment] = None, _prims: dict[str, prim.Prim] = None,
                 _blocks: dict[str, block.Block] = None,
                 # Stage only:
                 _tempo: int | float = 60, _video_state: str = "off", _video_transparency: int | float = 50,
                 _text_to_speech_language: str = "en", _visible: bool = True,
                 # Sprite only:
                 _x: int | float = 0, _y: int | float = 0, _size: int | float = 100, _direction: int | float = 90,
                 _draggable: bool = False, _rotation_style: str = "all around",

                 *, _project: project.Project = None):
        """
        Represents a sprite or the stage (known internally as a Target)
        https://en.scratch-wiki.info/wiki/Scratch_File_Format#Targets
        """
        # Defaulting for list parameters
        if _broadcasts is None:
            _broadcasts = []
        if _variables is None:
            _variables = []
        if _lists is None:
            _lists = []
        if _costumes is None:
            _costumes = []
        if _sounds is None:
            _sounds = []
        if _comments is None:
            _comments = []
        if _prims is None:
            _prims = []
        if _blocks is None:
            _blocks = []

        self.is_stage = is_stage
        self.name = name
        self.current_costume = _current_costume
        self.layer_order = _layer_order
        self.volume = _volume

        self.broadcasts = _broadcasts
        self.variables = _variables
        self.lists = _lists
        self._local_globals = []

        self.costumes = _costumes
        self.sounds = _sounds

        self.comments = _comments
        self.prims = _prims
        self.blocks = _blocks

        self.tempo = _tempo
        self.video_state = _video_state
        self.video_transparency = _video_transparency
        self.text_to_speech_language = _text_to_speech_language
        self.visible = _visible
        self.x, self.y = _x, _y
        self.size = _size
        self.direction = _direction
        self.draggable = _draggable
        self.rotation_style = _rotation_style

        super().__init__(_project)

        # Assign sprite
        for iterable in (self.vlbs, self.comments, self.assets, self.prims.values(), self.blocks.values()):
            for sub_component in iterable:
                sub_component.sprite = self

    def link_prims(self):
        """
        Link primitives to corresponding VLB objects (requires project attribute)
        """
        assert self.project is not None

        # Link prims to vars/lists/broadcasts
        for _id, _prim in self.prims.items():
            if _prim.is_vlb:
                if _prim.type.name == "variable":
                    _prim.value = self.find_variable(_prim.id, "id")
                elif _prim.type.name == "list":
                    _prim.value = self.find_list(_prim.id, "id")
                elif _prim.type.name == "broadcast":
                    _prim.value = self.find_broadcast(_prim.id, "id")
                else:
                    # This should never happen
                    raise exceptions.BadVLBPrimitiveError(f"{_prim} claims to be VLB, but is {_prim.type.name}")
                if _prim.value is None:
                    if not self.project:
                        new_vlb = vlb.construct(_prim.type.name.lower(), _prim.id, _prim.name)
                        self._add_local_global(new_vlb)
                        _prim.value = new_vlb
                    else:
                        new_vlb = vlb.construct(_prim.type.name.lower(), _prim.id, _prim.name)
                        self.stage.add_vlb(new_vlb)

                        warnings.warn(f"Prim<name={_prim.name!r}, id={_prim.name!r}> has unknown {_prim.type.name} id; adding as global variable")
                _prim.name = None
                _prim.id = None

    def link_blocks(self):
        """
        Link blocks to sprite/to other blocks
        """
        for _block_id, _block in self.blocks.items():
            _block.link_using_sprite()

    def _add_local_global(self, _vlb: base.NamedIDComponent):
        self._local_globals.append(_vlb)
        _vlb.sprite = self

    def add_variable(self, _variable: vlb.Variable):
        self.variables.append(_variable)
        _variable.sprite = self

    def add_list(self, _list: vlb.List):
        self.variables.append(_list)
        _list.sprite = self

    def add_broadcast(self, _broadcast: vlb.Broadcast):
        self.variables.append(_broadcast)
        _broadcast.sprite = self

    def add_vlb(self, _vlb: base.NamedIDComponent):
        if isinstance(_vlb, vlb.Variable):
            self.add_variable(_vlb)
        elif isinstance(_vlb, vlb.List):
            self.add_list(_vlb)
        elif isinstance(_vlb, vlb.Broadcast):
            self.add_broadcast(_vlb)
        else:
            warnings.warn(f"Invalid 'VLB' {_vlb} of type: {type(_vlb)}")

    def __repr__(self):
        return f"Sprite<{self.name}>"

    @property
    def vlbs(self) -> list[base.NamedIDComponent]:
        return self.variables + self.lists + self.broadcasts

    @property
    def assets(self) -> list[asset.Costume | asset.Sound]:
        return self.costumes + self.sounds

    @property
    def stage(self) -> Sprite:
        return self.project.stage

    @staticmethod
    def from_json(data: dict):
        _is_stage = data["isStage"]
        _name = data["name"]
        _current_costume = data.get("currentCostume", 1)
        _layer_order = data.get("layerOrder", 1)
        _volume = data.get("volume", 100)

        # Read VLB
        def read_idcomponent(attr_name: str, cls: type[base.IDComponent]):
            _vlbs = []
            for _vlb_id, _vlb_data in data.get(attr_name, {}).items():
                _vlbs.append(cls.from_json((_vlb_id, _vlb_data)))
            return _vlbs

        _variables = read_idcomponent("variables", vlb.Variable)
        _lists = read_idcomponent("lists", vlb.List)
        _broadcasts = read_idcomponent("broadcasts", vlb.Broadcast)

        # Read assets
        _costumes = []
        for _costume_data in data.get("costumes", []):
            _costumes.append(asset.Costume.from_json(_costume_data))
        _sounds = []
        for _sound_data in data.get("sounds", []):
            _sounds.append(asset.Sound.from_json(_sound_data))

        # Read comments
        _comments = read_idcomponent("comments", comment.Comment)

        # Read blocks/prims
        _prims = {}
        _blocks = {}
        for _block_id, _block_data in data.get("blocks", {}).items():
            if isinstance(_block_data, list):
                # Prim
                _prims[_block_id] = prim.Prim.from_json(_block_data)
            else:
                # Block
                _blocks[_block_id] = block.Block.from_json(_block_data)

        # Stage/sprite specific vars
        _tempo, _video_state, _video_transparency, _text_to_speech_language = (None,) * 4
        _visible, _x, _y, _size, _direction, _draggable, _rotation_style = (None,) * 7
        if _is_stage:
            _tempo = data["tempo"]
            _video_state = data["videoState"]
            _video_transparency = data["videoTransparency"]
            _text_to_speech_language = data["textToSpeechLanguage"]
        else:
            _visible = data["visible"]
            _x = data["x"]
            _y = data["y"]
            _size = data["size"]
            _direction = data["direction"]
            _draggable = data["draggable"]
            _rotation_style = data["rotationStyle"]

        return Sprite(_is_stage, _name, _current_costume, _layer_order, _volume, _broadcasts, _variables, _lists,
                      _costumes,
                      _sounds, _comments, _prims, _blocks,

                      _tempo, _video_state, _video_transparency, _text_to_speech_language,
                      _visible, _x, _y, _size, _direction, _draggable, _rotation_style
                      )

    def to_json(self) -> dict:
        pass

    # Finding/getting from list/dict attributes
    def find_variable(self, value: str, by: str = "name", multiple: bool = False) -> vlb.Variable | list[vlb.Variable]:
        _ret = []
        by = by.lower()
        for _variable in self.variables + self._local_globals:
            if not isinstance(_variable, vlb.Variable):
                continue

            if by == "id":
                compare = _variable.id
            else:
                # Defaulting
                compare = _variable.name
            if compare == value:
                if multiple:
                    _ret.append(_variable)
                else:
                    return _variable
        # Search in stage for global variables
        if self.project:
            if not self.is_stage:
                if multiple:
                    _ret += self.stage.find_variable(value, by, True)
                else:
                    return self.stage.find_variable(value, by)

        if multiple:
            return _ret

    def find_list(self, value: str, by: str = "name", multiple: bool = False) -> vlb.List | list[vlb.List]:
        _ret = []
        by = by.lower()
        for _list in self.lists + self._local_globals:
            if not isinstance(_list, vlb.List):
                continue
            if by == "id":
                compare = _list.id
            else:
                # Defaulting
                compare = _list.name
            if compare == value:
                if multiple:
                    _ret.append(_list)
                else:
                    return _list
        # Search in stage for global lists
        if self.project:
            if not self.is_stage:
                if multiple:
                    _ret += self.stage.find_list(value, by, True)
                else:
                    return self.stage.find_list(value, by)

        if multiple:
            return _ret

    def find_broadcast(self, value: str, by: str = "name", multiple: bool = False) -> vlb.Broadcast | list[
        vlb.Broadcast]:
        _ret = []
        by = by.lower()
        for _broadcast in self.broadcasts + self._local_globals:
            if not isinstance(_broadcast, vlb.Broadcast):
                continue
            if by == "id":
                compare = _broadcast.id
            else:
                # Defaulting
                compare = _broadcast.name
            if compare == value:
                if multiple:
                    _ret.append(_broadcast)
                else:
                    return _broadcast
        # Search in stage for global broadcasts
        if self.project:
            if not self.is_stage:
                if multiple:
                    _ret += self.stage.find_broadcast(value, by, True)
                else:
                    return self.stage.find_broadcast(value, by)

        if multiple:
            return _ret

    def find_block(self, value: str | Any, by: str = "opcode", multiple: bool = False) -> block.Block | list[
        block.Block]:
        _ret = []
        by = by.lower()
        for _block_id, _block in self.blocks.items():
            compare = None
            if by == "id":
                compare = _block_id
            elif by == "argument ids":
                if _block.mutation is not None:
                    compare = _block.mutation.argument_ids
            else:
                # Defaulting
                compare = _block.opcode

            if compare == value:
                if multiple:
                    _ret.append(_block)
                else:
                    return _block
        # Search in stage for global variables
        if self.project:
            if not self.is_stage:
                if multiple:
                    _ret += self.stage.find_block(value, by, True)
                else:
                    return self.stage.find_block(value, by)

        if multiple:
            return _ret
