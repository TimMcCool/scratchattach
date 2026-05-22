from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar, Optional, Self, Union, Any, Generic, TypeAlias, cast
import json

import requests

from scratchattach.utils import exceptions, commons, optional_async
from scratchattach.utils import requests as m_requests
from scratchattach._shared import http as shared_http
from . import session
from ..primitives import http

D = TypeVar("D")
C = TypeVar("C", bound="BaseSiteComponent")


class BaseSiteComponent(ABC, Generic[D]):
    _session: session.Session | session.UnauthSession
    update_api: str

    # @abstractmethod
    # def __init__(self):  # dataclasses do not implement __init__ directly
    #     pass

    async def update(self):
        """
        Updates the attributes of the object by performing an API response. Returns True if the update was successful.
        """
        async with self._session.http_session.request(
            self.update_method, self.update_api, shared_http.options().timeout(10).value
        ) as response:
            if response.status_code == 429:
                return "429"  # TODO: Check what this does and replace it

            response_json = await response.json()

            if response_json == {"response": "Too many requests"}:
                return "429"

            assert isinstance(response_json, dict)

            if "code" in response_json:
                return False

            return self._update_from_data(cast(D, response_json))

    async def updated(self) -> Self:
        await self.update()
        return self

    @abstractmethod
    def _update_from_data(self, data: D) -> bool:
        """
        Parses the API response that is fetched in the update-method. Class specific, must be overridden in classes inheriting from this one.
        """

    def _assert_auth(self) -> session.Session:
        if isinstance(self._session, session.UnauthSession):
            raise exceptions.Unauthenticated(
                "You need to use session.connect_xyz (NOT get_xyz) in order to perform this operation."
            )
        return self._session

    @classmethod
    def _get_object(
        cls, identificator_name, identificator, NotFoundException, session=None
    ) -> Self:
        # Internal function: Generalization of the process ran by get_user, get_studio etc.
        # Builds an object of class that is inheriting from BaseSiteComponent
        # # Class must inherit from BaseSiteComponent
        from scratchattach.site import project

        try:
            use_class: type = cls
            if cls is project.PartialProject:
                use_class = project.Project
                assert issubclass(use_class, cls)
            _object = use_class(**{identificator_name: identificator, "_session": session})
            r = _object.update()
            if r == "429":
                raise exceptions.Response429(
                    "Your network is blocked or rate-limited by Scratch.\n"
                    "If you're using an online IDE like replit.com, try running the code on your computer."
                )
            if not r:
                # Target is unshared. The cases that this can happen in are hardcoded:
                if cls is project.PartialProject:  # Case: Target is an unshared project.
                    _object = project.PartialProject(
                        **{identificator_name: identificator, "shared": False, "_session": session}
                    )
                    assert isinstance(_object, cls)
                    return _object
                else:
                    raise NotFoundException
            else:
                return _object
        except KeyError as e:
            raise NotFoundException(f"Key error at key {e} when reading API response")
        except Exception as e:
            raise e

    def _make_linked_object(
        self, identificator_id, identificator, cls: type[C], not_found_exception
    ) -> C:
        """
        Internal function for making a linked object (authentication kept) based on an identificator (like a project id or username)
        Class must inherit from BaseSiteComponent
        """
        return cls._get_object(
            identificator_id, identificator, not_found_exception, self._session
        )

    def supply_data_dict(self, data: D) -> bool:
        return self._update_from_data(data)

    update_method: shared_http.HTTPMethod = shared_http.HTTPMethod.GET
    """
    HTTP method for getting updated information for this component
    """
