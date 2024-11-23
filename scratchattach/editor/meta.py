import re

from . import base

DEFAULT_VM = "0.1.0"
DEFAULT_AGENT = "scratchattach.editor by https://scratch.mit.edu/users/timmccool/"
DEFAULT_PLATFORM = {
    "name": "scratchattach",
    "url": "https://github.com/timMcCool/scratchattach/"
}

EDIT_META = True
META_SET_PLATFORM = False


class Meta(base.ProjectPart):
    def __init__(self, semver: str = "3.0.0", vm: str = DEFAULT_VM, agent: str = DEFAULT_AGENT,
                 platform: dict = None):
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

        if self.platform is not None:
            _json["platform"] = self.platform
        return _json

    @staticmethod
    def from_json(data):
        if data is None:
            data = ""

        semver = data["semver"]
        vm = data.get("vm")
        agent = data.get("agent")
        platform = data.get("platform")

        if EDIT_META or vm is None:
            vm = DEFAULT_VM
        if EDIT_META or agent is None:
            agent = DEFAULT_AGENT
        if META_SET_PLATFORM and (EDIT_META or platform is None):
            platform = DEFAULT_PLATFORM.copy()

        return Meta(semver, vm, agent, platform)
