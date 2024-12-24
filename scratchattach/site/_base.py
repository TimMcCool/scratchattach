from __future__ import annotations

from abc import ABC, abstractmethod

import requests
from ..utils import exceptions, commons
from types import FunctionType


class BaseSiteComponent(ABC):
    @abstractmethod
    def __init__(self):
        self._session = None
        self._cookies = None
        self._headers = None
        self.update_API = None

    def update(self):
        """
        Updates the attributes of the object by performing an API response. Returns True if the update was successful.
        """
        response = self.update_function(
            self.update_API,
            headers=self._headers,
            cookies=self._cookies, timeout=10
        )
        # Check for 429 error:
        # Note, this is a bit naïve
        if "429" in str(response):
            return "429"

        if response.text == '{\n  "response": "Too many requests"\n}':
            return "429"

        # If no error: Parse JSON:
        response = response.json()
        if "code" in response:
            return False

        return self._update_from_dict(response)

    @abstractmethod
    def _update_from_dict(self, data) -> bool:
        """
        Parses the API response that is fetched in the update-method. Class specific, must be overridden in classes inheriting from this one.
        """
        pass

    def _assert_auth(self):
        if self._session is None:
            raise exceptions.Unauthenticated(
                "You need to use session.connect_xyz (NOT get_xyz) in order to perform this operation.")

    def _make_linked_object(self, identificator_id, identificator, Class, NotFoundException) -> BaseSiteComponent:
        """
        Internal function for making a linked object (authentication kept) based on an identificator (like a project id or username)
        Class must inherit from BaseSiteComponent
        """
        return commons._get_object(identificator_id, identificator, Class, NotFoundException, self._session)

    update_function: FunctionType = requests.get
    """
    Internal function run on update. Function is a method of the 'requests' module/class
    """
