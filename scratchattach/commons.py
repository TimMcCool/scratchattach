"""Common functions used by various internal modules"""

import requests
from . import exceptions

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "x-csrftoken": "a",
    "x-requested-with": "XMLHttpRequest",
    "referer": "https://scratch.mit.edu",
} # headers recommended for accessing API endpoints that don't require verification

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

def _get_object(identificator_id, identificator, Class, NotFoundException):
    # Interal function: Generalization of the process ran by get_user, get_studio etc.
    try:
        _object = Class(**{identificator_id:identificator, "_session":None})
        if _object.update() == "429":
            raise(exceptions.Response429("Your network is blocked or rate-limited by Scratch.\nIf you're using an online IDE like replit.com, try running the code on your computer."))
        if not _object: # Target is unshared
            return False
        return _object
    except KeyError as e:
        raise(NotFoundException("Key error at key "+str(e)+" when reading API response"))
    except Exception as e:
        raise(e)

'''

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


def api_iterative_simple(
    url, limit, offset, max_req_limit=40, add_params="", headers=headers, cookies={}
):
    if offset < 0:
        raise exceptions.BadRequest("offset parameter must be >= 0")
    if limit < 0:
        raise exceptions.BadRequest("limit parameter must be >= 0")
    def fetch(o, l):
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
'''