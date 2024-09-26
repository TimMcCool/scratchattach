from abc import ABC, abstractmethod
import requests
from threading import Thread
from ..utils import exceptions

class BaseEventHandler(ABC):

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
