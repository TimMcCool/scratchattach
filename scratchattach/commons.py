"""v2 ready: Common functions and abstract classes used by various internal modules"""

from abc import ABC, abstractmethod
from . import exceptions
from threading import Thread
import requests
from . import exceptions

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

class BaseCommunityEntity(ABC):

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
                "You need to use session.connect_user (NOT get_user) in order to perform this operation.")

    def _make_linked_object(self, identificator_id, identificator, Class, NotFoundException):
        """
        Internal function for making a linked object (authentication kept) based on an identificator (like a project id or username)
        """
        try:
            _object = Class(**{identificator_id:identificator, "_session":self._session})
            _object.update()
            return _object
        except KeyError as e:
            raise(NotFoundException("Key error at key "+str(e)+" when reading API response"))
        except Exception as e:
            raise(e)

class BaseEventHandler(ABC):

    class Event:
        def __init__(self, **entries):
            self.__dict__.update(entries)

    def start(self, *, update_interval = 0.1, thread=True):
        """
        Starts the cloud event handler.

        Keyword Arguments:
            update_interval (float): The clouddata log is continuosly checked for cloud updates. This argument provides the interval between these checks.
            thread (boolean): Whether the event handler should be run in a thread.
        """
        if self.running is False:
            self.update_interval = update_interval
            self.running = True
            if "on_ready" in self._events:
                self._events["on_ready"]()
            if thread:
                self._thread = Thread(target=self._update, args=())
                self._thread.start()
            else:
                self._thread = None
                self._update()

    @abstractmethod
    def _update(self):
        pass

    def stop(self):
        """
        Permanently stops the cloud event handler.
        """
        if self._thread is not None:
            self.running = False
            self._thread.join()
            self._thread = None

    def pause(self):
        """
        Pauses the cloud event handler.
        """
        self.running = False

    def resume(self):
        """
        Resumes the cloud event handler.
        """
        if self.running is False:
            self.start(update_interval=self.update_interval, thread=True)

    def event(self, function):
        """
        Decorator function. Adds a cloud event.
        """
        self._events[function.__name__] = function

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
