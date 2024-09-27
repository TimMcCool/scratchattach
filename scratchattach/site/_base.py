from abc import ABC, abstractmethod
import requests
from threading import Thread
from ..utils import exceptions, commons

class BaseSiteComponent(ABC):

    def update(self):
        """
        Updates the attributes of the object. Returns True if the update was successful.
        """
        response = self.update_function(
            self.update_API,
            headers = self._headers,
            cookies = self._cookies, timeout=10
        )
        # Check for 429 error:
        if "429" in str(response):
            return "429"
        if response.text == '{\n  "response": "Too many requests"\n}':
            return "429"
        # If no error: Parse JSON:
        response = response.json()
        return self._update_from_dict(response)

    @abstractmethod
    def _update_from_dict(self, data) -> bool:
        pass

    def _assert_auth(self):
        if self._session is None:
            raise exceptions.Unauthenticated(
                "You need to use session.connect_xyz (NOT get_xyz) in order to perform this operation.")

    def _make_linked_object(self, identificator_id, identificator, Class, NotFoundException):
        """
        Internal function for making a linked object (authentication kept) based on an identificator (like a project id or username)
        """
        return commons._get_object(identificator_id, identificator, Class, NotFoundException, self._session)

