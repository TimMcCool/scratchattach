from __future__ import annotations

import json
import time
import logging

from ._base import BaseSiteComponent
from ..utils import exceptions
from ..utils.requests import Requests as requests



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

    def __init__(self, **entries):
        # Set attributes every BackpackAsset object needs to have:
        self._session = None

        # Update attributes from entries dict:
        self.__dict__.update(entries)

    def update(self):
        print("Warning: BackpackAsset objects can't be updated")
        return False  # Objects of this type cannot be updated

    
    def _update_from_dict(self, data) -> bool:
        try:
            self.id = data["id"]
        except Exception:
            pass
        try:
            self.type = data["type"]
        except Exception:
            pass
        try:
            self.mime = data["mime"]
        except Exception:
            pass
        try:
            self.name = data["name"]
        except Exception:
            pass
        try:
            self.filename = data["body"]
        except Exception:
            pass
        try:
            self.thumbnail_url = "https://backpack.scratch.mit.edu/" + data["thumbnail"]
        except Exception:
            pass
        try:
            self.download_url = "https://backpack.scratch.mit.edu/" + data["body"]
        except Exception:
            pass
        return True

    @property
    def _data_bytes(self) -> bytes:
        try:
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

    def download(self, *, fp: str = ''):
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
