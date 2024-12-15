"""
scratchattach.editor (sbeditor v2) - a library for all things sb3
"""

from .asset import Asset, Costume, Sound
from .project import Project
from .extension import Extensions, Extension
from .mutation import Mutation, Argument, parse_proc_code
from .meta import Meta, set_meta_platform
from .sprite import Sprite
from .block import Block
from .prim import Prim, PrimTypes
from .backpack_json import load_script as load_script_from_backpack
from .twconfig import TWConfig, is_valid_twconfig
from .inputs import Input, ShadowStatuses
from .field import Field
from .vlb import Variable, List, Broadcast
from .comment import Comment
from .monitor import Monitor

from .build_defaulting import add_chain, add_comment, add_block
