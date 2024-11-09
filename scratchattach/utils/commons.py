"""v2 ready: Common functions used by various internal modules"""
from types import FunctionType
from typing import Final, Any, TYPE_CHECKING

from . import exceptions
from .requests import Requests as requests

if TYPE_CHECKING:
    # Having to do this is quite inelegant, but this is commons.py, so this is done to avoid cyclic imports
    from ..site._base import BaseSiteComponent

headers: Final = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "x-csrftoken": "a",
    "x-requested-with": "XMLHttpRequest",
    "referer": "https://scratch.mit.edu",
}  # headers recommended for accessing API endpoints that don't require verification

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


def api_iterative_data(fetch_func: FunctionType, limit: int, offset: int, max_req_limit: int = 40,
                       unpack: bool = True):
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
                  _headers: dict = None, cookies: dict = None):
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


def _get_object(identificator_name, identificator, Class, NotFoundException, session=None) -> 'BaseSiteComponent':
    # Internal function: Generalization of the process ran by get_user, get_studio etc.
    # Builds an object of class that is inheriting from BaseSiteComponent
    # # Class must inherit from BaseSiteComponent
    try:
        _object = Class(**{identificator_name: identificator, "_session": session})
        r = _object.update()
        if r == "429":
            raise exceptions.Response429(
                "Your network is blocked or rate-limited by Scratch.\n"
                "If you're using an online IDE like replit.com, try running the code on your computer.")
        if not r:
            # Target is unshared. The cases that this can happen in are hardcoded:
            from ..site import project
            if Class is project.Project:  # Case: Target is an unshared project.
                return project.PartialProject(**{identificator_name: identificator,
                                                 "shared": False, "_session": session})
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


def parse_object_list(raw, Class, session=None, primary_key="id") -> list:
    results = []
    for raw_dict in raw:
        try:
            _obj = Class(**{primary_key: raw_dict[primary_key], "_session": session})
            _obj._update_from_dict(raw_dict)
            results.append(_obj)
        except Exception as e:
            print("Warning raised by scratchattach: failed to parse ", raw_dict, "error", e)
    return results
