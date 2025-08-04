from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar, Optional, Self, Union, Any

import requests
from scratchattach.utils import exceptions, commons, optional_async
from scratchattach.utils import requests as m_requests
from . import session

C = TypeVar("C", bound="BaseSiteComponent")
class BaseSiteComponent(ABC):
    _session: Optional[session.Session]
    update_api: str
    _headers: dict[str, str]
    _cookies: dict[str, str]
    oa_http_session: Optional[m_requests.OAHTTPSession] = None

    # @abstractmethod
    # def __init__(self):  # dataclasses do not implement __init__ directly
    #     pass

    def update(self):
        """
        Updates the attributes of the object by performing an API response. Returns True if the update was successful.
        """
        response = self.update_function(
            self.update_api,
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
    
    def updated(self) -> Self:
        self.update()
        return self

    @abstractmethod
    def _update_from_dict(self, data) -> bool:
        """
        Parses the API response that is fetched in the update-method. Class specific, must be overridden in classes inheriting from this one.
        """

    def _assert_auth(self):
        if self._session is None:
            raise exceptions.Unauthenticated(
                "You need to use session.connect_xyz (NOT get_xyz) in order to perform this operation.")

    def _make_linked_object(self, identificator_id, identificator, Class: type[C], NotFoundException) -> C:
        """
        Internal function for making a linked object (authentication kept) based on an identificator (like a project id or username)
        Class must inherit from BaseSiteComponent
        """
        return commons._get_object(identificator_id, identificator, Class, NotFoundException, self._session)

    update_function = requests.get
    """
    Internal function run on update. Function is a method of the 'requests' module/class
    """
    
    def _make_request(
        self,
        method: Union[m_requests.HTTPMethod, str],
        url: str,
        *,
        cookies: Optional[dict[str, str]] = None,
        headers: Optional[dict[str, str]] = None,
        params: Optional[dict[str, str]] = None,
        data: Optional[Union[dict[str, str], str]] = None,
        json: Optional[Any] = None
    ) -> optional_async.CARequest:
        if self.oa_http_session is None:
            raise ValueError("This BaseSiteComponent has no oa_http_session.")
        return self.oa_http_session.request(method, url, cookies=cookies, headers=headers, params=params, data=data, json=json)
