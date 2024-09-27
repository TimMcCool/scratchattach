from abc import ABC, abstractmethod
from ..utils.requests import Requests as requests
from threading import Thread
from ..utils import exceptions
import traceback

class BaseEventHandler(ABC):
            
    def start(self, *, thread=True, ignore_exceptions=True):
        """
        Starts the cloud event handler.

        Keyword Arguments:
            update_interval (float): The clouddata log is continuosly checked for cloud updates. This argument provides the interval between these checks.
            thread (boolean): Whether the event handler should be run in a thread.
        """
        if self.running is False:
            self.ignore_exceptions = ignore_exceptions
            self.running = True
            if "on_ready" in self._events:
                self._events["on_ready"]()
            if thread:
                self._thread = Thread(target=self._update, args=())
                self._thread.start()
            else:
                self._thread = None
                self._update()
    
    def call_event(self, event_name, args=[]):
        if event_name in self._events:
            try:
                self._events[event_name](*args)
            except Exception as e:
                if self.ignore_exceptions:
                    print(
                        f"Warning: Caught error in event '{event_name}' - Full error below"
                    )
                    try:
                        traceback.print_exc()
                    except Exception:
                        print(e)
                else:
                    raise(e)

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