"""v2 ready: Common functions used by various internal modules"""
from __future__ import annotations

from typing import Optional, Final, Any, TypeVar, Callable, TYPE_CHECKING, Union
from threading import Lock

from . import exceptions
from .requests import Requests as requests

from ..site import _base

headers: Final = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "x-csrftoken": "a",
    "x-requested-with": "XMLHttpRequest",
    "referer": "https://scratch.mit.edu",
}
empty_project_json: Final = {
    'targets': [
        {
            'isStage': True,
            'name': 'Stage',
            'variables': {
                '`jEk@4|i[#Fk?(8x)AV.-my variable': [
                    'my variable',
                    0,
                ],
            },
            'lists': {},
            'broadcasts': {},
            'blocks': {},
            'comments': {},
            'currentCostume': 0,
            'costumes': [
                {
                    'name': '',
                    'bitmapResolution': 1,
                    'dataFormat': 'svg',
                    'assetId': '14e46ec3e2ba471c2adfe8f119052307',
                    'md5ext': '14e46ec3e2ba471c2adfe8f119052307.svg',
                    'rotationCenterX': 0,
                    'rotationCenterY': 0,
                },
            ],
            'sounds': [],
            'volume': 100,
            'layerOrder': 0,
            'tempo': 60,
            'videoTransparency': 50,
            'videoState': 'on',
            'textToSpeechLanguage': None,
        },
    ],
    'monitors': [],
    'extensions': [],
    'meta': {
        'semver': '3.0.0',
        'vm': '2.3.0',
        'agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                 'Chrome/124.0.0.0 Safari/537.36',
    },
}


def api_iterative_data(fetch_func: Callable[[int, int], list], limit: int, offset: int, max_req_limit: int = 40,
                       unpack: bool = True) -> list:
    """
    Iteratively gets data by calling fetch_func with a moving offset and a limit.
    Once fetch_func returns None, the retrieval is completed.
    """
    if limit is None:
        limit = max_req_limit

    end = offset + limit
    api_data = []
    for offs in range(offset, end, max_req_limit):
        # Mimic actual scratch by only requesting the max amount
        data = fetch_func(offs, max_req_limit)
        if data is None:
            break

        if unpack:
            api_data.extend(data)
        else:
            api_data.append(data)

        if len(data) < max_req_limit:
            break

    api_data = api_data[:limit]
    return api_data


def api_iterative(url: str, *, limit: int, offset: int, max_req_limit: int = 40, add_params: str = "",
                  _headers: Optional[dict] = None, cookies: Optional[dict] = None):
    """
    Function for getting data from one of Scratch's iterative JSON API endpoints (like /users/<user>/followers, or /users/<user>/projects)
    """
    if _headers is None:
        _headers = headers.copy()
    if cookies is None:
        cookies = {}

    if offset < 0:
        raise exceptions.BadRequest("offset parameter must be >= 0")
    if limit < 0:
        raise exceptions.BadRequest("limit parameter must be >= 0")

    def fetch(off: int, lim: int):
        """
        Performs a single API request
        """
        resp = requests.get(
            f"{url}?limit={lim}&offset={off}{add_params}", headers=_headers, cookies=cookies, timeout=10
        ).json()

        if not resp:
            return None
        if resp == {"code": "BadRequest", "message": ""}:
            raise exceptions.BadRequest("The passed arguments are invalid")
        return resp

    api_data = api_iterative_data(
        fetch, limit, offset, max_req_limit=max_req_limit, unpack=True
    )
    return api_data

def _get_object(identificator_name, identificator, __class: type[C], NotFoundException, session=None) -> C:
    # Internal function: Generalization of the process ran by get_user, get_studio etc.
    # Builds an object of class that is inheriting from BaseSiteComponent
    # # Class must inherit from BaseSiteComponent
    from ..site import project
    try:
        use_class: type = __class
        if __class is project.PartialProject:
            use_class = project.Project
            assert issubclass(use_class, __class)
        _object = use_class(**{identificator_name: identificator, "_session": session})
        r = _object.update()
        if r == "429":
            raise exceptions.Response429(
                "Your network is blocked or rate-limited by Scratch.\n"
                "If you're using an online IDE like replit.com, try running the code on your computer.")
        if not r:
            # Target is unshared. The cases that this can happen in are hardcoded:
            if __class is project.PartialProject:  # Case: Target is an unshared project.
                _object = project.PartialProject(**{identificator_name: identificator,
                                                 "shared": False, "_session": session})
                assert isinstance(_object, __class)
                return _object
            else:
                raise NotFoundException
        else:
            return _object
    except KeyError as e:
        raise NotFoundException(f"Key error at key {e} when reading API response")
    except Exception as e:
        raise e


def webscrape_count(raw, text_before, text_after, cls: type = int) -> int | Any:
    return cls(raw.split(text_before)[1].split(text_after)[0])


if TYPE_CHECKING:
    C = TypeVar("C", bound=_base.BaseSiteComponent)

def parse_object_list(raw, __class: type[C], session=None, primary_key="id") -> list[C]:
    results = []
    for raw_dict in raw:
        try:
            _obj = __class(**{primary_key: raw_dict[primary_key], "_session": session})
            _obj._update_from_dict(raw_dict)
            results.append(_obj)
        except Exception as e:
            print("Warning raised by scratchattach: failed to parse ", raw_dict, "error", e)
    return results


class LockEvent:
    """
    Can be waited on and triggered. Not to be confused with threading.Event, which has to be reset.
    """
    locks: list[Lock]
    def __init__(self):
        self.locks = []
        self.use_locks = Lock()

    def wait(self, blocking: bool = True, timeout: Optional[Union[int, float]] = None) -> bool:
        """
        Wait for the event.
        """
        timeout = -1 if timeout is None else timeout
        if not blocking:
            timeout = 0
        return self.on().acquire(timeout=timeout)

    def trigger(self):
        """
        Trigger all threads waiting on this event to continue.
        """
        with self.use_locks:
            for lock in self.locks:
                try:
                    lock.release() # Unlock the lock once to trigger the event.
                except RuntimeError:
                    lock.acquire(timeout=0) # Lock the lock again.
            for lock in self.locks.copy():
                try:
                    lock.release() # Unlock the lock once more to make sure it was waited on.
                    self.locks.remove(lock)
                except RuntimeError:
                    lock.acquire(timeout=0) # Lock the lock again.

    def on(self) -> Lock:
        """
        Return a lock that will unlock once the event takes place.
        """
        lock = Lock()
        with self.use_locks:
            self.locks.append(lock)
        lock.acquire(timeout=0)
        return lock

def get_class_sort_mode(mode: str) -> tuple[str, str]:
    """
    Returns the sort mode for the given mode for classes only
    """
    ascsort = ''
    descsort = ''

    mode = mode.lower()
    if mode == "last created":
        pass
    elif mode == "students":
        descsort = "student_count"
    elif mode == "a-z":
        ascsort = "title"
    elif mode == "z-a":
        descsort = "title"

    return ascsort, descsort
