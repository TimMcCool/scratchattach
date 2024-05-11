"""Common functions used by various internal modules"""

import requests


def api_iterative_data(fetch_func, limit, offset, max_req_limit=40, unpack=True):
    """
    Iteratively gets data by calling fetch_func with a moving offset and a limit.
    Once fetch_func returns None, the retrieval is completed.
    """
    if limit is None:
        limit = max_req_limit
    assert offset >= 0
    assert limit >= 0
    end = offset + limit
    api_data = []
    for offs in range(offset, end, max_req_limit):
        print(offs, max_req_limit)
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
    assert len(api_data) <= limit
    return api_data


def api_iterative_simple(url, limit, offset, max_req_limit=40, add_params=""):
    def fetch(o, l):
        resp = requests.get(f"{url}?limit={l}&offset={o}{add_params}").json()
        if not resp or resp == {"code": "BadRequest", "message": ""}:
            return None
        return resp

    api_data = api_iterative_data(
        fetch, limit, offset, max_req_limit=max_req_limit, unpack=True
    )
    return api_data
