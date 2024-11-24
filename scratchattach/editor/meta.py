from __future__ import annotations

import re
from dataclasses import dataclass

from . import base, commons


@dataclass(init=True, repr=True)
class PlatformMeta(base.JSONSerializable):
    name: str = None
    url: str = None

    def __bool__(self):
        return self.name is not None or self.url is not None

    def to_json(self) -> dict:
        _json = {"name": self.name, "url": self.url}
        commons.remove_nones(_json)
        return _json

    @staticmethod
    def from_json(data: dict | None):
        if data is None:
            return PlatformMeta()
        else:
            return PlatformMeta(data.get("name"), data.get("url"))


DEFAULT_VM = "0.1.0"
DEFAULT_AGENT = "scratchattach.editor by https://scratch.mit.edu/users/timmccool/"
DEFAULT_PLATFORM = PlatformMeta("scratchattach", "https://github.com/timMcCool/scratchattach/")

EDIT_META = True
META_SET_PLATFORM = False


class Meta(base.JSONSerializable):
    def __init__(self, semver: str = "3.0.0", vm: str = DEFAULT_VM, agent: str = DEFAULT_AGENT,
                 platform: PlatformMeta = None):
        """
        Represents metadata of the project
        https://en.scratch-wiki.info/wiki/Scratch_File_Format#Metadata
        """
        if platform is None and META_SET_PLATFORM:
            platform = DEFAULT_PLATFORM.copy()

        # Thanks to TurboWarp for this pattern ↓↓↓↓, I just copied it
        if re.match("^([0-9]+\\.[0-9]+\\.[0-9]+)($|-)", vm) is None:
            raise ValueError(
                f"\"{vm}\" does not match pattern \"^([0-9]+\\.[0-9]+\\.[0-9]+)($|-)\" - maybe try \"0.0.0\"?")

        self.semver = semver
        self.vm = vm
        self.agent = agent
        self.platform = platform

    def __repr__(self):
        data = f"{self.semver} : {self.vm} : {self.agent}"
        if self.platform:
            data += f": {self.platform}"

        return f"Meta<{data}>"

    def to_json(self):
        _json = {
            "semver": self.semver,
            "vm": self.vm,
            "agent": self.agent
        }

        if self.platform:
            _json["platform"] = self.platform.to_json()
        return _json

    @staticmethod
    def from_json(data):
        if data is None:
            data = ""

        semver = data["semver"]
        vm = data.get("vm")
        agent = data.get("agent")
        platform = PlatformMeta.from_json(data.get("platform"))

        if EDIT_META or vm is None:
            vm = DEFAULT_VM

        if EDIT_META or agent is None:
            agent = DEFAULT_AGENT

        if EDIT_META:
            if META_SET_PLATFORM and not platform:
                platform = DEFAULT_PLATFORM.copy()

        return Meta(semver, vm, agent, platform)
