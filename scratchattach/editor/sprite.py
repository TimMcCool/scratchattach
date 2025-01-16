from __future__ import annotations

import json
import warnings
from io import BytesIO, TextIOWrapper
from typing import Optional, Any, BinaryIO
from zipfile import ZipFile
from typing import Iterable, TYPE_CHECKING
from . import base, project, vlb, asset, comment, prim, block, commons, build_defaulting
if TYPE_CHECKING:
    from . import asset

class Sprite(base.ProjectSubcomponent, base.JSONExtractable):
    def __init__(self, is_stage: bool = False, name: str = '', _current_costume: int = 1, _layer_order: Optional[int] = None,
                 _volume: int = 100,
                 _broadcasts: Optional[list[vlb.Broadcast]] = None,
                 _variables: Optional[list[vlb.Variable]] = None, _lists: Optional[list[vlb.List]] = None,
                 _costumes: Optional[list[asset.Costume]] = None, _sounds: Optional[list[asset.Sound]] = None,
                 _comments: Optional[list[comment.Comment]] = None, _prims: Optional[dict[str, prim.Prim]] = None,
                 _blocks: Optional[dict[str, block.Block]] = None,
                 # Stage only:
                 _tempo: int | float = 60, _video_state: str = "off", _video_transparency: int | float = 50,
                 _text_to_speech_language: str = "en", _visible: bool = True,
                 # Sprite only:
                 _x: int | float = 0, _y: int | float = 0, _size: int | float = 100, _direction: int | float = 90,
                 _draggable: bool = False, _rotation_style: str = "all around",

                 *, _project: Optional[project.Project] = None):
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
            _prims = {}
        if _blocks is None:
            _blocks = {}

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

        self.asset_data = []

        super().__init__(_project)

        # Assign sprite
        for iterable in (self.vlbs, self.comments, self.assets, self.prims.values(), self.blocks.values()):
            for sub_component in iterable:
                sub_component.sprite = self

    def __repr__(self):
        return f"Sprite<{self.name}>"

    def __enter__(self):
        build_defaulting.stack_add_sprite(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        build_defaulting.pop_sprite(self)

    def link_subcomponents(self):
        self.link_prims()
        self.link_blocks()
        self.link_comments()

    def link_prims(self):
        """
        Link primitives to corresponding VLB objects (requires project attribute)
        """
        for _prim in self.prims.values():
            _prim.link_using_sprite()

    def link_blocks(self):
        """
        Link blocks to sprite/to other blocks
        """
        for _block_id, _block in self.blocks.items():
            _block.link_using_sprite()

    def link_comments(self):
        for _comment in self.comments:
            _comment.link_using_sprite()

    def add_local_global(self, _vlb: base.NamedIDComponent):
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

    def add_block(self, _block: block.Block | prim.Prim) -> block.Block | prim.Prim:
        if _block.sprite is self:
            if _block in self.blocks.values():
                return _block

        _block.sprite = self

        if isinstance(_block, block.Block):
            self.blocks[self.new_id] = _block
            _block.link_using_sprite()

        elif isinstance(_block, prim.Prim):
            self.prims[self.new_id] = _block
            _block.link_using_sprite()

        return _block

    def add_chain(self, *chain: Iterable[block.Block | prim.Prim]) -> block.Block | prim.Prim:
        """
        Adds a list of blocks to the sprite **AND RETURNS THE FIRST BLOCK**
        :param chain:
        :return:
        """
        chain = tuple(chain)

        _prev = self.add_block(chain[0])

        for _block in chain[1:]:
            _prev = _prev.attach_block(_block)

        return chain[0]

    def add_comment(self, _comment: comment.Comment) -> comment.Comment:
        _comment.sprite = self
        if _comment.id is None:
            _comment.id = self.new_id

        self.comments.append(_comment)
        _comment.link_using_sprite()

        return _comment

    def remove_block(self, _block: block.Block):
        for key, val in self.blocks.items():
            if val is _block:
                del self.blocks[key]
                return

    @property
    def folder(self):
        return commons.get_folder_name(self.name)

    @property
    def name_nfldr(self):
        return commons.get_name_nofldr(self.name)

    @property
    def vlbs(self) -> list[base.NamedIDComponent]:
        """
        :return: All vlbs associated with the sprite. No local globals are added
        """
        return self.variables + self.lists + self.broadcasts

    @property
    def assets(self) -> list[asset.Costume | asset.Sound]:
        return self.costumes + self.sounds

    @property
    def stage(self) -> Sprite:
        return self.project.stage

    @property
    def new_id(self):
        return commons.gen_id()

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
        _json = {
            "isStage": self.is_stage,
            "name": self.name,
            "currentCostume": self.current_costume,
            "volume": self.volume,
            "layerOrder": self.layer_order,

            "variables": {_variable.id: _variable.to_json() for _variable in self.variables},
            "lists": {_list.id: _list.to_json() for _list in self.lists},
            "broadcasts": {_broadcast.id: _broadcast.to_json() for _broadcast in self.broadcasts},

            "blocks": {_block_id: _block.to_json() for _block_id, _block in (self.blocks | self.prims).items()},
            "comments": {_comment.id: _comment.to_json() for _comment in self.comments},

            "costumes": [_costume.to_json() for _costume in self.costumes],
            "sounds": [_sound.to_json() for _sound in self.sounds]
        }

        if self.is_stage:
            _json.update({
                "tempo": self.tempo,
                "videoTransparency": self.video_transparency,
                "videoState": self.video_state,
                "textToSpeechLanguage": self.text_to_speech_language
            })
        else:
            _json.update({
                "visible": self.visible,

                "x": self.x, "y": self.y,
                "size": self.size,
                "direction": self.direction,

                "draggable": self.draggable,
                "rotationStyle": self.rotation_style
            })

        return _json

    # Finding/getting from list/dict attributes
    def find_asset(self, value: str, by: str = "name", multiple: bool = False, a_type: Optional[type]=None) -> asset.Asset | asset.Sound | asset.Costume | list[asset.Asset | asset.Sound | asset.Costume]:
        if a_type is None:
            a_type = asset.Asset

        _ret = []
        by = by.lower()
        for _asset in self.assets:
            if not isinstance(_asset, a_type):
                continue

            # Defaulting
            compare = getattr(_asset, by)

            if compare == value:
                if multiple:
                    _ret.append(_asset)
                else:
                    return _asset

        if multiple:
            return _ret

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

    def find_vlb(self, value: str, by: str = "name",
                 multiple: bool = False) -> vlb.Variable | vlb.List | vlb.Broadcast | list[
        vlb.Variable | vlb.List | vlb.Broadcast]:
        if multiple:
            return self.find_variable(value, by, True) + \
                self.find_list(value, by, True) + \
                self.find_broadcast(value, by, True)
        else:
            _ret = self.find_variable(value, by)
            if _ret is not None:
                return _ret
            _ret = self.find_list(value, by)
            if _ret is not None:
                return _ret
            return self.find_broadcast(value, by)

    def find_block(self, value: str | Any, by: str, multiple: bool = False) -> block.Block | prim.Prim | list[
        block.Block | prim.Prim]:
        _ret = []
        by = by.lower()
        for _block_id, _block in (self.blocks | self.prims).items():
            _block: block.Block | prim.Prim

            is_block = isinstance(_block, block.Block)
            is_prim = isinstance(_block, prim.Prim)

            compare = None
            if by == "id":
                compare = _block_id
            elif by == "argument ids":
                if is_prim:
                    continue

                if _block.mutation is not None:
                    compare = _block.mutation.argument_ids
            elif by == "opcode":
                if is_prim:
                    continue

                # Defaulting
                compare = _block.opcode
            else:
                if is_block:
                    compare = _block.opcode
                else:
                    compare = _block.value

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

    def export(self, fp: Optional[str] = None, *, export_as_zip: bool = True):
        if fp is None:
            fp = commons.sanitize_fn(f"{self.name}.sprite3")

        data = self.to_json()

        if export_as_zip:
            with ZipFile(fp, "w") as archive:
                for _asset in self.assets:
                    asset_file = _asset.asset_file
                    if asset_file.filename not in archive.namelist():
                        archive.writestr(asset_file.filename, asset_file.data)

                archive.writestr("sprite.json", json.dumps(data))
        else:
            with open(fp, "w") as json_file:
                json.dump(data, json_file)

    @property
    def all_ids(self):
        ret = []
        for _vlb in self.vlbs + self._local_globals:
            ret.append(_vlb.id)
        for iterator in self.blocks.keys(), self.prims.keys():
            ret += list(iterator)

        return ret
    @staticmethod
    def load_json(data: str | bytes | TextIOWrapper | BinaryIO, load_assets: bool = True, _name: Optional[str] = None):
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
            # For if the sprite3 is just JSON (e.g. if it's exported from scratchattach)
            if commons.is_valid_json(data):
                json_str = data

            else:
                with ZipFile(data) as archive:
                    json_str = archive.read("sprite.json")

                    # Also load assets
                    if load_assets:

                        for filename in archive.namelist():
                            if filename != "sprite.json":
                                md5_hash = filename.split('.')[0]

                                asset_data.append(
                                    asset.AssetFile(filename, archive.read(filename), md5_hash)
                                )
                    else:
                        warnings.warn(
                            "Loading sb3 without loading assets. When exporting the project, there may be errors due to assets not being uploaded to the Scratch website")

            return _name, asset_data, json_str

    @classmethod
    def from_sprite3(cls, data: str | bytes | TextIOWrapper | BinaryIO, load_assets: bool = True, _name: Optional[str] = None):
        """
        Load a project from an .sb3 file/bytes/file path
        """
        _name, asset_data, json_str = cls.load_json(data, load_assets, _name)
        data = json.loads(json_str)

        sprite = cls.from_json(data)
        # Sprites already have names, so we probably don't want to set it
        # sprite.name = _name
        sprite.asset_data = asset_data
        return sprite
