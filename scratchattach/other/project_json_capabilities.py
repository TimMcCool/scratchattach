"""Project JSON reading and editing capabilities.
This code is still in BETA, there are still bugs and potential consistency issues to be fixed. New features will be added."""

# Note: You may want to make this into multiple files for better organisation
from __future__ import annotations

import hashlib
import json
import random
import string
import zipfile
from abc import ABC, abstractmethod
from ..utils import exceptions
from ..utils.commons import empty_project_json
from ..utils.requests import Requests as requests
# noinspection PyPep8Naming
def load_components(json_data: list, ComponentClass: type, target_list: list):
    for element in json_data:
        component = ComponentClass()
        component.from_json(element)
        target_list.append(component)
class ProjectBody:
    class BaseProjectBodyComponent(ABC):
        def __init__(self, **entries):
            # Attributes every object needs to have:
            self.id = None
            # Update attributes from entries dict:
            self.__dict__.update(entries)
        @abstractmethod
        def from_json(self, data: dict):
            pass
        @abstractmethod
        def to_json(self):
            pass
        def _generate_new_id(self):
            """
            Generates a new id and updates the id.
            Warning:
                When done on Block objects, the next_id attribute of the parent block and the parent_id attribute of the next block will NOT be updated by this method.
            """
            self.id = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
    class Block(BaseProjectBodyComponent):
        # Thanks to @MonkeyBean2 for some scripts
        def from_json(self, data: dict):
            self.opcode = data["opcode"]  # The name of the block
            self.next_id = data.get("next", None)  # The id of the block attached below this block
            self.parent_id = data.get("parent", None)  # The id of the block that this block is attached to
            self.input_data = data.get("inputs", None)  # The blocks inside of the block (if the block is a loop or an if clause for example)
            self.fields = data.get("fields", None)  # The values inside the block's inputs
            self.shadow = data.get("shadow", False)  # Whether the block is displayed with a shadow
            self.topLevel = data.get("topLevel", False)  # Whether the block has no parent
            self.mutation = data.get("mutation", None)  # For custom blocks
            self.x = data.get("x", None)  # x position if topLevel
            self.y = data.get("y", None)  # y position if topLevel
        def to_json(self):
            output = {"opcode": self.opcode, "next": self.next_id, "parent": self.parent_id, "inputs": self.input_data,
                      "fields": self.fields, "shadow": self.shadow, "topLevel": self.topLevel,
                      "mutation": self.mutation, "x": self.x, "y": self.y}
            return {k: v for k, v in output.items() if v}
        def attached_block(self):
            return self.sprite.block_by_id(self.next_id)
        def previous_block(self):
            return self.sprite.block_by_id(self.parent_id)
        def top_level_block(self):
            block = self
            return block
        def previous_chain(self):
            # to implement: a method that detects circular block chains (to make sure this method terminates)
            chain = []
            block = self
            while block.parent_id is not None:
                block = block.previous_block()
                chain.insert(0, block)
            return chain
        def attached_chain(self):
            chain = []
            block = self
            while block.next_id is not None:
                block = block.attached_block()
                chain.append(block)
            return chain
        def complete_chain(self):
            return self.previous_chain() + [self] + self.attached_chain()
        def duplicate_single_block(self):
            new_block = ProjectBody.Block(**self.__dict__)
            new_block.parent_id = None
            new_block.next_id = None
            new_block._generate_new_id()
            self.sprite.blocks.append(new_block)
            return new_block
        def duplicate_chain(self):
            blocks_to_dupe = [self] + self.attached_chain()
            duped = []
            for i in range(len(blocks_to_dupe)):
                new_block = ProjectBody.Block(**blocks_to_dupe[i].__dict__)
                new_block.parent_id = None
                new_block.next_id = None
                new_block._generate_new_id()
                if i != 0:
                    new_block.parent_id = duped[i - 1].id
                    duped[i - 1].next_id = new_block.id
                duped.append(new_block)
            self.sprite.blocks += duped
            return duped
        def _reattach(self, new_parent_id, new_next_id_of_old_parent):
            if self.parent_id is not None:
                old_parent_block = self.sprite.block_by_id(self.parent_id)
                self.sprite.blocks.remove(old_parent_block)
                old_parent_block.next_id = new_next_id_of_old_parent
                self.sprite.blocks.append(old_parent_block)
            self.parent_id = new_parent_id
            if self.parent_id is not None:
                new_parent_block = self.sprite.block_by_id(self.parent_id)
                self.sprite.blocks.remove(new_parent_block)
                new_parent_block.next_id = self.id
                self.sprite.blocks.append(new_parent_block)
            self.topLevel = new_parent_id is None
        def reattach_single_block(self, new_parent_id):
            old_parent_id = str(self.parent_id)
            self._reattach(new_parent_id, self.next_id)
            if self.next_id is not None:
                old_next_block = self.sprite.block_by_id(self.next_id)
                self.sprite.blocks.remove(old_next_block)
                old_next_block.parent_id = old_parent_id
                self.sprite.blocks.append(old_next_block)
            self.next_id = None
        def reattach_chain(self, new_parent_id):
            self._reattach(new_parent_id, None)
        def delete_single_block(self):
            self.sprite.blocks.remove(self)
            self.reattach_single_block(None, self.next_id)
        def delete_chain(self):
            self.sprite.blocks.remove(self)
            self.reattach_chain(None)
            to_delete = self.attached_chain()
            for block in to_delete:
                self.sprite.blocks.remove(block)
        def inputs_as_blocks(self):
            if self.input_data is None:
                return None
            inputs = []
            for input in self.input_data:
                inputs.append(self.sprite.block_by_id(self.input_data[input][1]))
    class Sprite(BaseProjectBodyComponent):
        def from_json(self, data: dict):
            self.isStage = data["isStage"]
            self.name = data["name"]
            self.id = self.name  # Sprites are uniquely identifiable through their name
            self.variables = []
            for variable_id in data["variables"]:  # self.lists is a dict with the list_id as key and info as value
                pvar = ProjectBody.Variable(id=variable_id)
                pvar.from_json(data["variables"][variable_id])
                self.variables.append(pvar)
            self.lists = []
            for list_id in data["lists"]:  # self.lists is a dict with the list_id as key and info as value
                plist = ProjectBody.List(id=list_id)
                plist.from_json(data["lists"][list_id])
                self.lists.append(plist)
            self.broadcasts = data["broadcasts"]
            self.blocks = []
            for block_id in data["blocks"]:  # self.blocks is a dict with the block_id as key and block content as value
                if isinstance(data["blocks"][block_id],
                              dict):  # Sometimes there is a weird list at the end of the blocks list. This list is ignored
                    block = ProjectBody.Block(id=block_id, sprite=self)
                    block.from_json(data["blocks"][block_id])
                    self.blocks.append(block)
            self.comments = data["comments"]
            self.currentCostume = data["currentCostume"]
            self.costumes = []
            load_components(data["costumes"], ProjectBody.Asset, self.costumes)  # load lists
            self.sounds = []
            load_components(data["sounds"], ProjectBody.Asset, self.sounds)  # load lists
            self.volume = data["volume"]
            self.layerOrder = data["layerOrder"]
            if self.isStage:
                self.tempo = data.get("tempo", None)
                self.videoTransparency = data.get("videoTransparency", None)
                self.videoState = data.get("videoState", None)
                self.textToSpeechLanguage = data.get("textToSpeechLanguage", None)
            else:
                self.visible = data.get("visible", None)
                self.x = data.get("x", None)
                self.y = data.get("y", None)
                self.size = data.get("size", None)
                self.direction = data.get("direction", None)
                self.draggable = data.get("draggable", None)
                self.rotationStyle = data.get("rotationStyle", None)
        def to_json(self):
            return_data = dict(self.__dict__)
            if "projectBody" in return_data:
                return_data.pop("projectBody")
            return_data.pop("id")
            return_data["variables"] = {}
            for variable in self.variables:
                return_data["variables"][variable.id] = variable.to_json()
            return_data["lists"] = {}
            for plist in self.lists:
                return_data["lists"][plist.id] = plist.to_json()
            return_data["blocks"] = {}
            for block in self.blocks:
                return_data["blocks"][block.id] = block.to_json()
            return_data["costumes"] = [custome.to_json() for custome in self.costumes]
            return_data["sounds"] = [sound.to_json() for sound in self.sounds]
            return return_data
        def variable_by_id(self, variable_id):
            matching = list(filter(lambda x: x.id == variable_id, self.variables))
            if matching == []:
                return None
            return matching[0]
        def list_by_id(self, list_id):
            matching = list(filter(lambda x: x.id == list_id, self.lists))
            if matching == []:
                return None
            return matching[0]
        def variable_by_name(self, variable_name):
            matching = list(filter(lambda x: x.name == variable_name, self.variables))
            if matching == []:
                return None
            return matching[0]
        def list_by_name(self, list_name):
            matching = list(filter(lambda x: x.name == list_name, self.lists))
            if matching == []:
                return None
            return matching[0]
        def block_by_id(self, block_id):
            matching = list(filter(lambda x: x.id == block_id, self.blocks))
            if matching == []:
                return None
            return matching[0]
        # -- Functions to modify project contents --
        def create_sound(self, asset_content, *, name="new sound", dataFormat="mp3", rate=4800, sampleCount=4800):
            data = asset_content if isinstance(asset_content, bytes) else open(asset_content, "rb").read()
            new_asset_id = hashlib.md5(data).hexdigest()
            new_asset = ProjectBody.Asset(assetId=new_asset_id, name=name, id=new_asset_id, dataFormat=dataFormat,
                                          rate=rate, sampleCound=sampleCount, md5ext=new_asset_id + "." + dataFormat,
                                          filename=new_asset_id + "." + dataFormat)
            self.sounds.append(new_asset)
            if not hasattr(self, "projectBody"):
                print(
                    "Warning: Since there's no project body connected to this object, the new sound asset won't be uploaded to Scratch")
            elif self.projectBody._session is None:
                print(
                    "Warning: Since there's no login connected to this object, the new sound asset won't be uploaded to Scratch")
            else:
                self._session.upload_asset(data, asset_id=new_asset_id, file_ext=dataFormat)
            return new_asset
        def create_costume(self, asset_content, *, name="new costume", dataFormat="svg", rotationCenterX=0,
                           rotationCenterY=0):
            data = asset_content if isinstance(asset_content, bytes) else open(asset_content, "rb").read()
            new_asset_id = hashlib.md5(data).hexdigest()
            new_asset = ProjectBody.Asset(assetId=new_asset_id, name=name, id=new_asset_id, dataFormat=dataFormat,
                                          rotationCenterX=rotationCenterX, rotationCenterY=rotationCenterY,
                                          md5ext=new_asset_id + "." + dataFormat,
                                          filename=new_asset_id + "." + dataFormat)
            self.costumes.append(new_asset)
            if not hasattr(self, "projectBody"):
                print(
                    "Warning: Since there's no project body connected to this object, the new costume asset won't be uploaded to Scratch")
            elif self.projectBody._session is None:
                print(
                    "Warning: Since there's no login connected to this object, the new costume asset won't be uploaded to Scratch")
            else:
                self._session.upload_asset(data, asset_id=new_asset_id, file_ext=dataFormat)
            return new_asset
        def create_variable(self, name, *, value=0, is_cloud=False):
            new_var = ProjectBody.Variable(name=name, value=value, is_cloud=is_cloud)
            self.variables.append(new_var)
            return new_var
        def create_list(self, name, *, value=[]):
            new_list = ProjectBody.List(name=name, value=value)
            self.lists.append(new_list)
            return new_list
        def add_block(self, block, *, parent_id=None):
            block.parent_id = None
            block.next_id = None
            if parent_id is not None:
                block.reattach_single_block(parent_id)
            self.blocks.append(block)
        def add_block_chain(self, block_chain, *, parent_id=None):
            parent = parent_id
            for block in block_chain:
                self.add_block(block, parent_id=parent)
                parent = str(block.id)
    class Variable(BaseProjectBodyComponent):
        def __init__(self, **entries):
            super().__init__(**entries)
            if self.id is None:
                self._generate_new_id()
        def from_json(self, data: list):
            self.name = data[0]
            self.saved_value = data[1]
            self.is_cloud = len(data) == 3
        def to_json(self):
            if self.is_cloud:
                return [self.name, self.saved_value, True]
            else:
                return [self.name, self.saved_value]
        def make_cloud_variable(self):
            self.is_cloud = True
    class List(BaseProjectBodyComponent):
        def __init__(self, **entries):
            super().__init__(**entries)
            if self.id is None:
                self._generate_new_id()
        def from_json(self, data: list):
            self.name = data[0]
            self.saved_content = data[1]
        def to_json(self):
            return [self.name, self.saved_content]
    class Monitor(BaseProjectBodyComponent):
        def from_json(self, data: dict):
            self.__dict__.update(data)
        def to_json(self):
            return_data = dict(self.__dict__)
            if "projectBody" in return_data:
                return_data.pop("projectBody")
            return return_data
        def target(self):
            if not hasattr(self, "projectBody"):
                print("Can't get represented object because the origin projectBody of this monitor is not saved")
                return
            if "VARIABLE" in self.params:
                return self.projectBody.sprite_by_name(self.spriteName).variable_by_name(self.params["VARIABLE"])
            if "LIST" in self.params:
                return self.projectBody.sprite_by_name(self.spriteName).list_by_name(self.params["LIST"])
    class Asset(BaseProjectBodyComponent):
        def from_json(self, data: dict):
            self.__dict__.update(data)
            self.id = self.assetId
            self.filename = self.md5ext
            self.download_url = f"https://assets.scratch.mit.edu/internalapi/asset/{self.filename}"
        def to_json(self):
            return_data = dict(self.__dict__)
            return_data.pop("filename")
            return_data.pop("id")
            return_data.pop("download_url")
            return return_data
        def download(self, *, filename=None, dir=""):
            if not (dir.endswith("/") or dir.endswith("\\")):
                dir = dir + "/"
            try:
                if filename is None:
                    filename = str(self.filename)
                response = requests.get(
                    self.download_url,
                    timeout=10,
                )
                open(f"{dir}{filename}", "wb").write(response.content)
            except Exception:
                raise (
                    exceptions.FetchError(
                        "Failed to download asset"
                    )
                )
    def __init__(self, *, sprites=[], monitors=[], extensions=[], meta=[{"agent": None}], _session=None):
        # sprites are called "targets" in the initial API response
        self.sprites = sprites
        self.monitors = monitors
        self.extensions = extensions
        self.meta = meta
        self._session = _session
    def from_json(self, data: dict):
        """
        Imports the project data from a dict that contains the raw project json
        """
        # Load sprites:
        self.sprites = []
        load_components(data["targets"], ProjectBody.Sprite, self.sprites)
        # Save origin of sprite in Sprite object:
        for sprite in self.sprites:
            sprite.projectBody = self
            # Load monitors:
        self.monitors = []
        load_components(data["monitors"], ProjectBody.Monitor, self.monitors)
        # Save origin of monitor in Monitor object:
        for monitor in self.monitors:
            monitor.projectBody = self
        # Set extensions and meta attributs:
        self.extensions = data["extensions"]
        self.meta = data["meta"]
    def to_json(self):
        """
        Returns a valid project JSON dict with the contents of this project
        """
        return_data = {}
        return_data["targets"] = [sprite.to_json() for sprite in self.sprites]
        return_data["monitors"] = [monitor.to_json() for monitor in self.monitors]
        return_data["extensions"] = self.extensions
        return_data["meta"] = self.meta
        return return_data
    # -- Functions to get info --
    def blocks(self):
        return [block for sprite in self.sprites for block in sprite.blocks]
    def block_count(self):
        return len(self.blocks())
    def assets(self):
        return [sound for sprite in self.sprites for sound in sprite.sounds] + [costume for sprite in self.sprites for
                                                                                costume in sprite.costumes]
    def asset_count(self):
        return len(self.assets())
    def variable_by_id(self, variable_id):
        for sprite in self.sprites:
            r = sprite.variable_by_id(variable_id)
            if r is not None:
                return r
    def list_by_id(self, list_id):
        for sprite in self.sprites:
            r = sprite.list_by_id(list_id)
            if r is not None:
                return r
    def sprite_by_name(self, sprite_name):
        matching = list(filter(lambda x: x.name == sprite_name, self.sprites))
        if matching == []:
            return None
        return matching[0]
    def user_agent(self):
        return self.meta["agent"]
    def save(self, *, filename=None, dir=""):
        """
        Saves the project body to the given directory.
        Args:
            filename (str): The name that will be given to the downloaded file.
            dir (str): The path of the directory the file will be saved in.
        """
        if not (dir.endswith("/") or dir.endswith("\\")):
            dir = dir + "/"
        if filename is None:
            filename = "project"
        filename = filename.replace(".sb3", "")
        with open(f"{dir}{filename}.sb3", "w") as d:
            json.dump(self.to_json(), d, indent=4)
def get_empty_project_pb():
    pb = ProjectBody()
    pb.from_json(empty_project_json)
    return pb
def get_pb_from_dict(project_json: dict):
    pb = ProjectBody()
    pb.from_json(project_json)
    return pb
def _load_sb3_file(path_to_file):
    try:
        with open(path_to_file, "r") as r:
            return json.loads(r.read())
    except Exception as e:
        with zipfile.ZipFile(path_to_file, 'r') as zip_ref:
            # Check if the file exists in the zip
            if "project.json" in zip_ref.namelist():
                # Read the file as bytes
                with zip_ref.open("project.json") as file:
                    return json.loads(file.read())
            else:
                raise ValueError("specified sb3 archive doesn't contain project.json")
def read_sb3_file(path_to_file):
    pb = ProjectBody()
    pb.from_json(_load_sb3_file(path_to_file))
    return pb
def download_asset(asset_id_with_file_ext, *, filename=None, dir=""):
    if not (dir.endswith("/") or dir.endswith("\\")):
        dir = dir + "/"
    try:
        if filename is None:
            filename = str(asset_id_with_file_ext)
        response = requests.get(
            "https://assets.scratch.mit.edu/" + str(asset_id_with_file_ext),
            timeout=10,
        )
        open(f"{dir}{filename}", "wb").write(response.content)
    except Exception:
        raise (
            exceptions.FetchError(
                "Failed to download asset"
            )
        )

# The method for uploading an asset by id requires authentication and can be found in the site.session.Session class
