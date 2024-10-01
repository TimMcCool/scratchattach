"""v2 ready: Project JSON reading and editing capabilities#
This code is still in BETA, there are still bugs and potential consistency issues to be fixed"""

import random
import string
from abc import ABC, abstractmethod
from ..utils import exceptions
from ..utils.requests import Requests as requests

def load_components(json_data:list, ComponentClass, target_list):
    target_list = []
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
        def from_json(self, data:dict):
            pass

        @abstractmethod
        def to_json(self):
            pass


    class Block(BaseProjectBodyComponent):
        
        # Thanks to @MonkeyBean2 for some scripts

        def from_json(self, data: dict):
            self.opcode = data["opcode"] # The name of the block 
            self.next_id = data["next"] # The id of the block attached below this block
            self.parent_id = data["parent"] # The id of the block that this block is attached to
            self.input_data = data["inputs"] # The blocks inside of the block (if the block is a loop or an if clause for example)
            self.fields = data["fields"] # The values inside the block's inputs
            self.shadow = data["shadow"] # Whether the block is displayed with a shadow
            self.topLevel = data["topLevel"]
            self.mutation = data["mutation"]
            self.x = data.get("x", 0)
            self.y = data.get("y", 0)
            
        def to_json(self):
            return {"opcode":self.opcode,"next":self.next_id,"parent":self.parent_id,"inputs":self.input_data,"fields":self.fields,"topLevel":self.topLevel,"shadow":self.shadow,"x":self.x,"y":self.y}
        
        def attached_block(self):
            return self.sprite.block_by_id(self.next_id)

        def previous_block(self):
            return self.sprite.block_by_id(self.parent_id)

        def top_level_block(self):
            block = self
            while block.parent_id is not None:
                block = self.previous_block()
            return block

        def previous_chain(self):
            chain = []
            block = self
            while block.parent_id is not None:
                block = self.previous_block()
                chain.insert(0,block)
            return chain

        def attached_chain(self):
            chain = []
            block = self
            while block.next_id is not None:
                block = self.next_block()
                chain.append(block)
            return chain

        def complete_chain(self):
            return self.previous_chain() + [self] + self.attached_chain()
    
        def generate_new_id(self):
            self.id = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
            
        def duplicate_single_block(self):
            new_block = self.Block(self.__dict__)
            new_block.parent_id = None
            new_block.next_id = None
            new_block.generate_new_id()
            self.sprite.blocks.append(new_block)
        
        def duplicate_chain(self):
            blocks_to_dupe = [self] + self.attached_chain()
            duped = []
            for i in range(len(blocks_to_dupe)):
                new_block = self.Block(blocks_to_dupe[i].__dict__)
                new_block.parent_id = None
                new_block.next_id = None
                new_block.generate_new_id()
                if i != 0:
                    new_block.parent_id = duped[i-1].id
                    duped[i-1].next_id = new_block.id
                duped.append(new_block)
            self.sprite.blocks += duped

        def _reattach(self, new_parent_id, new_next_id_of_old_parent):
            if self.parent_id is not None:
                old_parent_block = self.sprite.block_by_id(self.parent_id)
                self.sprite.blocks.remove(old_parent_block)
                old_parent_block.next_id = new_next_id_of_old_parent
                self.sprite.blocks.append(old_parent_block)

            self.parent_id = new_parent_id

            new_parent_block = self.sprite.block_by_id(self.parent_id)
            self.sprite.blocks.remove(new_parent_block)
            new_parent_block.next_id = self.id
            self.sprite.blocks.append(new_parent_block)

            self.topLevel = new_parent_id is None

        def reattach_single_block(self, new_parent_id):
            old_parent_id = str(self.parent_id)
            self._reattach(new_parent_id, self.next_id)

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
            inputs = []
            for input in self.input_data:
                inputs.append(self.sprite.block_by_id(self.input_data[input][1]))


    class Sprite(BaseProjectBodyComponent):

        def from_json(self, data:dict):
            self.isStage = data["isStage"]
            self.name = data["name"]
            self.variables = []
            load_components(data["variables"], ProjectBody.Variable, self.variables) # load variables
            self.lists = []
            load_components(data["lists"], ProjectBody.List, self.lists) # load lists
            self.broadcasts = data["broadcasts"]
            self.blocks = []
            for block_id in self.blocks: #self.blocks is a dict with the block_id as key and block content as value
                block = ProjectBody.Block(id=block_id)
                block.from_json(self.blocks[block_id])
                self.blocks.append(block)
            self.comments = data["comments"]
            self.currentCostume = data["currentCostume"]
            self.costumes = []
            load_components(data["costumes"], ProjectBody.Asset, self.costumes) # load lists
            self.sounds = []
            load_components(data["sounds"], ProjectBody.Asset, self.sounds) # load lists
            self.volume = data["volume"]
            self.layerOrder = data["layerOrder"]
            self.visible = data.get("visible", None)
            self.x = data.get("x", None)
            self.y = data.get("y", None)
            self.size = data.get("size", None)
            self.direction = data.get("direction", None)
            self.draggable = data.get("draggable", None)
            self.rotationStyle = data.get("rotationStyle", None)

        def to_json(self):
            return_data = self.__dict__
            return_data["variables"] = [variable.to_json() for variable in self.variables]
            return_data["lists"] = [plist.to_json() for plist in self.lists]
            return_data["blocks"] = [block.to_json() for block in self.blocks]
            return_data["customes"] = [custome.to_json() for custome in self.customes]
            return_data["sounds"] = [sound.to_json() for sound in self.sounds]
            return return_data

        def variable_by_id(self, variable_id):
            matching = list(filter(lambda x : x.id == variable_id, self.variables))
            if matching == []:
                return None
            return matching[0]

        def list_by_id(self, list_id):
            matching = list(filter(lambda x : x.id == list_id, self.lists))
            if matching == []:
                return None
            return matching[0]

        def block_by_id(self, block_id):
            matching = list(filter(lambda x : x.id == block_id, self.blocks))
            if matching == []:
                return None
            return matching[0]

    class Variable(BaseProjectBodyComponent):

        def from_json(self, data:list):
            self.name = data[0]
            self.saved_value = data[1]
            self.is_cloud = len(data) == 2

        def to_json(self):
            if self.is_cloud:
                return [self.name, self.saved_content, True]
            else:
                return [self.name, self.saved_content]

    class List(BaseProjectBodyComponent):

        def from_json(self, data:list):
            self.name = data[0]
            self.saved_content = data[1]
        
        def to_json(self):
            return [self.name, self.saved_content]
        
    class Monitor(BaseProjectBodyComponent):

        def from_json(self, data:dict):
            self.__dict__.update(data)
            if "VARIABLE" in data["params"]:
                self.represented_object = self.projectBody.variable_by_id(data["params"]["VARIABLE"])
            if "LIST" in data["params"]:
                self.represented_object = self.projectBody.variable_by_id(data["params"]["LIST"])

        def to_json(self):
            return_data = self.__dict__
            return_data.pop("represented_object")
            return return_data

    class Asset(BaseProjectBodyComponent):

        def from_json(self, data:dict):
            self.__dict__.update(data)
            self.id = self.assetId
            self.filename = self.md5ext
        
        def to_json(self):
            return_data = self.__dict__
            return_data.pop("filename")
            return_data.pop("id")
            return return_data

        def download(self, *, filename=None, dir=""):
            try:
                if filename is None:
                    filename = str(self.filename)
                response = requests.get(
                    f"https://assets.scratch.mit.edu/internalapi/asset/{self.filename}",
                    timeout=10,
                )
                open(f"{dir}{filename}", "wb").write(response.content)
            except Exception:
                raise (
                    exceptions.FetchError(
                        "Failed to download asset"
                    )
                )

    def __init__(self, *, sprites=[], monitors=[], extensions=[], meta=[{"agent":None}]):
        # sprites are called "targets" in the initial API response
        self.sprites = sprites
        self.monitors = monitors
        self.extensions = extensions
        self.meta = meta

    def from_json(self, data:dict):
        """
        Imports the project data from a dict that contains the raw project json
        """
        # Load sprites:
        self.sprites = []
        load_components(data["targets"], ProjectBody.Sprite, self.sprites)
        # Load monitors:
        self.monitors = []
        load_components(data["monitors"], ProjectBody.Monitor, self.monitors)
        # Save origin of monitor in Monitor object:
        for monitor in self.monitors:
            monitor.projectBody = self
        # Set extensions and meta attributs: 
        self.extensions = data["meta"]
        self.meta = data["meta"]

    def to_json(self):
        """
        Returns a valid project JSON dict with the contents of this project
        """
        return_data = {}
        return_data["targets"] = {}
        for sprite in self.sprites:
            return_data["targets"][sprite.id] = sprite.to_json()
        return_data["monitors"] = {}
        for monitor in self.monitors:
            return_data["monitors"][monitor.id] = monitor.to_json()
        return_data["extensions"] = self.extensions
        return_data["meta"] = self.meta
        return return_data

    def block_count(self):
        return len(self.blocks)
    
    def assets(self):
        return len([sound for sprite in self.sprites for sound in sprite.sounds]) + ([costume for sprite in self.sprites for costume in sprite.costumes])

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
    
    def user_agent(self):
        return self.meta["user_agent"]