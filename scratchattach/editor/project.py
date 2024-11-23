import json
from io import BytesIO, TextIOWrapper
from typing import Any, Iterable
from zipfile import ZipFile

from . import base, meta, extension, monitor


class Project(base.ProjectPart):
    def __init__(self, _meta: meta.Meta = None, _extensions: Iterable[extension.Extension] = (),
                 _monitors: Iterable[monitor.Monitor] = ()):
        if _meta is None:
            _meta = meta.Meta()

        self.meta = _meta
        self.extensions = _extensions
        self.monitors = _monitors

    def to_json(self) -> dict | list | Any:
        pass

    @staticmethod
    def from_json(data: dict | list | Any):
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

        return Project(_meta, _extensions, _monitors)

    @staticmethod
    def from_sb3(data: str | bytes | TextIOWrapper):
        """
        Load a project from an sb3 file/bytes/file path
        """
        if isinstance(data, bytes):
            data = BytesIO(data)

        elif isinstance(data, str):
            data = open(data, "rb")
        with data:
            try:
                return Project.from_json(json.load(data))
            except ValueError:
                with ZipFile(data) as archive:
                    data = json.loads(archive.read("project.json"))
                    return Project.from_json(data)
