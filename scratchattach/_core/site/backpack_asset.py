from __future__ import annotations

import json
import time
import logging
import warnings

from dataclasses import dataclass
from typing import Any, TYPE_CHECKING

from ._base import BaseSiteComponent
from scratchattach.utils import exceptions
from scratchattach.utils.requests import requests

if TYPE_CHECKING:
    from scratchattach import session


@dataclass
class BackpackAsset(BaseSiteComponent):
    """
    Represents an asset from the backpack.

    Attributes:

    :.id:

    :.type: The asset type (costume, script etc.)

    :.mime: The format in which the content of the backpack asset is saved

    :.name: The name of the backpack asset

    :.filename: Filename of the file containing the content of the backpack asset

    :.thumbnail_url: Link that leads to the asset's thumbnail (the image shown in the backpack UI)

    :.download_url: Link that leads to a file containing the content of the backpack asset
    """

    id: str
    _session: session.Session | None = None
    type: str | None = None
    mime: str | None = None
    name: str | None = None
    filename: str | None = None
    thumbnail_url: str | None = None
    download_url: str | None = None

    def __repr__(self) -> str:
        return f"BackpackAsset({self.filename})"

    def update(self):
        warnings.warn("Warning: BackpackAsset objects can't be updated")
        return False  # Objects of this type cannot be updated

    def _update_from_data(self, data: dict[str, str]) -> bool:
        self.id = data.get("id", self.id)
        self.type = data.get("type", self.type)
        self.mime = data.get("mime", self.mime)
        self.name = data.get("name", self.name)
        self.filename = data.get("body", self.filename)
        if "thumbnail" in data:
            self.thumbnail_url = "https://backpack.scratch.mit.edu/" + data["thumbnail"]
        if "body" in data:
            self.download_url = "https://backpack.scratch.mit.edu/" + data["body"]
        return True

    @property
    def _data_bytes(self) -> bytes:
        try:
            with requests.no_error_handling():
                return requests.get(self.download_url).content
        except Exception as e:
            raise exceptions.FetchError(f"Failed to download asset: {e}")

    @property
    def file_ext(self):
        return self.filename.split(".")[-1]

    @property
    def is_json(self):
        return self.file_ext == "json"

    @property
    def data(self) -> dict | list | int | None | str | bytes | float:
        if self.is_json:
            return json.loads(self._data_bytes)
        else:
            # It's either a zip
            return self._data_bytes

    def download(self, *, fp: str = ""):
        """
        Downloads the asset content to the given directory. The given filename is equal to the value saved in the .filename attribute.

        Args:
            fp (str): The path of the directory the file will be saved in.
        """
        if not (fp.endswith("/") or fp.endswith("\\")):
            fp = fp + "/"
        open(f"{fp}{self.filename}", "wb").write(self._data_bytes)

    def delete(self):
        self._assert_auth()

        return requests.delete(
            f"https://backpack.scratch.mit.edu/{self._session.username}/{self.id}",
            headers=self._session._headers,
            timeout=10,
        ).json()
