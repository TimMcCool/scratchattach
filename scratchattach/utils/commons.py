"""v2 ready: Common functions used by various internal modules"""

from . import exceptions
from threading import Thread
from .requests import Requests as requests

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "x-csrftoken": "a",
    "x-requested-with": "XMLHttpRequest",
    "referer": "https://scratch.mit.edu",
} # headers recommended for accessing API endpoints that don't require verification

empty_project_json = {
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
        'agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    },
}


def api_iterative_data(fetch_func, limit, offset, max_req_limit=40, unpack=True):
    """
    Iteratively gets data by calling fetch_func with a moving offset and a limit.
    Once fetch_func returns None, the retrieval is completed.
    """
    if limit is None:
        limit = max_req_limit
    end = offset + limit
    api_data = []
    for offs in range(offset, end, max_req_limit):
        d = fetch_func(
            offs, max_req_limit
        )  # Mimick actual scratch by only requesting the max amount
        if d is None:
            break
        if unpack:
            api_data.extend(d)
        else:
            api_data.append(d)
        if len(d) < max_req_limit:
            break
    api_data = api_data[:limit]
    return api_data

def api_iterative(
    url, *, limit, offset, max_req_limit=40, add_params="", headers=headers, cookies={}
):
    """
    Function for getting data from one of Scratch's iterative JSON API endpoints (like /users/<user>/followers, or /users/<user>/projects)
    """
    if offset < 0:
        raise exceptions.BadRequest("offset parameter must be >= 0")
    if limit < 0:
        raise exceptions.BadRequest("limit parameter must be >= 0")
    
    def fetch(o, l):
        """
        Performs a singla API request
        """
        resp = requests.get(
            f"{url}?limit={l}&offset={o}{add_params}", headers=headers, cookies=cookies, timeout=10
        ).json()
        if not resp:
            return None
        if resp == {"code": "BadRequest", "message": ""}:
            raise exceptions.BadRequest("the passed arguments are invalid")
        return resp

    api_data = api_iterative_data(
        fetch, limit, offset, max_req_limit=max_req_limit, unpack=True
    )
    return api_data

def _get_object(identificator_id, identificator, Class, NotFoundException, session=None):
    # Interal function: Generalization of the process ran by get_user, get_studio etc.
    try:
        _object = Class(**{identificator_id:identificator, "_session":session})
        r = _object.update()
        if r == "429":
            raise(exceptions.Response429("Your network is blocked or rate-limited by Scratch.\nIf you're using an online IDE like replit.com, try running the code on your computer."))
        if not r:
            # Target is unshared. The cases that this can happen in are hardcoded:
            from ..site import project
            if Class is project.Project: # Case: Target is an unshared project.
                return project.PartialProject(**{identificator_id:identificator, "_session":session})
            else:
                raise NotFoundException("Not found in API")
        else:
            return _object
    except KeyError as e:
        raise(NotFoundException("Key error at key "+str(e)+" when reading API response"))
    except Exception as e:
        raise(e)

def webscrape_count(raw, text_before, text_after):
    return int(raw.split(text_before)[1].split(text_after)[0])

def parse_object_list(raw, Class, session=None, primary_key="id"):
    results = []
    for raw_dict in raw:
        try:
            _obj = Class(**{primary_key:raw_dict[primary_key], "_session":session})
            _obj._update_from_dict(raw_dict)
            results.append(_obj)
        except Exception as e:
            print("Warning raised by scratchattach: failed to parse ", raw_dict, "error", e)
    return results