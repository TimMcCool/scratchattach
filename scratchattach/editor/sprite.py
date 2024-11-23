from __future__ import annotations

from . import base, project, vlb, asset, comment, prim
from ..utils import exceptions


class Sprite(base.ProjectSubcomponent):
    def __init__(self, is_stage: bool = False, name: str = '', _current_costume: int = 1, _layer_order: int = None,
                 _volume: int = 100,
                 _broadcasts: list[vlb.Broadcast] = None,
                 _variables: list[vlb.Variable] = None, _lists: list[vlb.List] = None,
                 _costumes: list[asset.Costume] = None, _sounds: list[asset.Sound] = None,
                 _comments: list[comment.Comment] = None, _prims: dict[str, prim.Prim] = None,
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

        self.is_stage = is_stage
        self.name = name
        self.current_costume = _current_costume
        self.layer_order = _layer_order
        self.volume = _volume

        self.broadcasts = _broadcasts
        self.variables = _variables
        self.lists = _lists

        self.costumes = _costumes
        self.sounds = _sounds

        self.comments = _comments
        self.prims = _prims

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
        for sub_component in self.vlbs + self.comments + self.assets:
            sub_component.sprite = self

        # Link prims to vars/lists/broadcasts
        for _id, _prim in self.prims.items():
            _prim.sprite = self
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
                _prim.name = None
                _prim.id = None

    def __repr__(self):
        return f"Sprite<{self.name}>"

    @property
    def vlbs(self) -> list[base.NamedIDComponent]:
        return self.variables + self.lists + self.broadcasts

    @property
    def assets(self) -> list[asset.Costume | asset.Sound]:
        return self.costumes + self.sounds

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
                pass

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
                      _sounds, _comments, _prims,

                      _tempo, _video_state, _video_transparency, _text_to_speech_language,
                      _visible, _x, _y, _size, _direction, _draggable, _rotation_style
                      )

    def to_json(self) -> dict:
        pass

    # Finding/getting from list/dict attributes
    def find_variable(self, value: str, by: str = "name", multiple: bool = False) -> vlb.Variable | list[vlb.Variable]:
        _ret = []
        by = by.lower()
        for _variable in self.variables:
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
        if multiple:
            return _ret

    def find_list(self, value: str, by: str = "name", multiple: bool = False) -> vlb.List | list[vlb.List]:
        _ret = []
        by = by.lower()
        for _list in self.lists:
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
        if multiple:
            return _ret

    def find_broadcast(self, value: str, by: str = "name", multiple: bool = False) -> vlb.Broadcast | list[vlb.Broadcast]:
        _ret = []
        by = by.lower()
        for _broadcast in self.broadcasts:
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
        if multiple:
            return _ret
