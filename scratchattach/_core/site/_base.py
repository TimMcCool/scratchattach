from __future__ import annotations
from collections.abc import Iterable

from abc import ABC, abstractmethod
from typing import TypeVar, Optional, Self, Union, Any, Generic, TypeAlias, cast, overload, Literal
import json

if "IS_ASYNC":
    from collections.abc import Callable, Awaitable
else:
    from collections.abc import Callable

from scratchattach.utils import exceptions, commons, optional_async
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
        cls,
        identificator_name,
        identificator,
        NotFoundException,
        session: session.Session | session.UnauthSession,
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
        return cls._get_object(identificator_id, identificator, not_found_exception, self._session)

    @classmethod
    def parse_object_list(
        cls,
        raw: list[D],
        /,
        session: session.Session | session.UnauthSession,
        primary_key: str = "id",
    ) -> list[Self]:
        results = []
        for raw_dict in raw:
            try:
                _obj = cls(
                    **{
                        primary_key: cast(dict[str, Any], raw_dict)[primary_key],
                        "_session": session,
                    }
                )
                # noinspection PyProtectedMember
                _obj._update_from_data(raw_dict)
                results.append(_obj)
            except Exception as e:
                print("Warning raised by scratchattach: failed to parse ", raw_dict, "error", e)
        return results

    def supply_data_dict(self, data: D) -> bool:
        return self._update_from_data(data)

    update_method: shared_http.HTTPMethod = shared_http.HTTPMethod.GET
    """
    HTTP method for getting updated information for this component
    """


F = TypeVar("F")

if "IS_ASYNC":  # type: ignore[misc]

    @overload
    async def api_iterative_data(
        fetch_func: Callable[[int, int], Awaitable[list[F] | None]],
        limit: int,
        offset: int,
        max_req_limit: int = 40,
        unpack: Literal[True] = True,
    ) -> list[F]: ...

    @overload
    async def api_iterative_data(
        fetch_func: Callable[[int, int], Awaitable[F | None]],
        limit: int,
        offset: int,
        max_req_limit: int = 40,
        unpack: Literal[False] = False,
    ) -> list[F]: ...
else:

    @overload
    def api_iterative_data(
        fetch_func: Callable[[int, int], list[F] | None],
        limit: int,
        offset: int,
        max_req_limit: int = 40,
        unpack: Literal[True] = True,
    ) -> list[F]: ...

    @overload
    def api_iterative_data(
        fetch_func: Callable[[int, int], F | None],
        limit: int,
        offset: int,
        max_req_limit: int = 40,
        unpack: Literal[False] = False,
    ) -> list[F]: ...


async def api_iterative_data(
    fetch_func: Callable[[int, int], Any],
    limit: int,
    offset: int,
    max_req_limit: int = 40,
    unpack: bool = True,
) -> list:
    """
    Iteratively gets data by calling fetch_func with a moving offset and a limit.
    Once fetch_func returns None, the retrieval is completed.
    """
    if limit is None:
        limit = max_req_limit

    end = offset + limit
    api_data: list[Any] = []
    for offs in range(offset, end, max_req_limit):
        # Mimic actual scratch by only requesting the max amount
        data = await fetch_func(offs, max_req_limit)
        if data is None:
            break

        if unpack:
            api_data.extend(data)
        else:
            api_data.append(data)

        if len(data) < max_req_limit:
            break

    return api_data[:limit]


async def api_iterative(
    session: session.Session | session.UnauthSession,
    url: str,
    *,
    limit: int,
    offset: int,
    max_req_limit: int = 40,
    add_params: str = "",
    _headers: Optional[Iterable[tuple[str, str]] | shared_http.SupportsItems[str, str]] = None,
    cookies: Optional[Iterable[tuple[str, str]] | shared_http.SupportsItems[str, str]] = None,
) -> list[F]:
    """
    Function for getting data from one of Scratch's iterative JSON API endpoints (like /users/<user>/followers, or /users/<user>/projects)
    """

    if offset < 0:
        raise exceptions.BadRequest("offset parameter must be >= 0")
    if limit < 0:
        raise exceptions.BadRequest("limit parameter must be >= 0")

    async def fetch(off: int, lim: int) -> list[F] | None:
        """
        Performs a single API request
        """
        async with session.http_session.get(
            f"{url}?limit={lim}&offset={off}{add_params}",
            shared_http.options()
            .headers(_headers)
            .cookies(cookies)
            .value
        ) as response:
            resp = cast(
                list[F],
                await response.json(),
            )

            if not resp:
                return None
            if resp == {"code": "BadRequest", "message": ""}:
                raise exceptions.BadRequest("The arguments passed are invalid")
            return resp

    return await api_iterative_data(fetch, limit, offset, max_req_limit=max_req_limit, unpack=True)
