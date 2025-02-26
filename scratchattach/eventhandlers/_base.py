from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from threading import Thread
from collections.abc import Callable
import traceback
from ..utils.requests import Requests as requests
from ..utils import exceptions

class BaseEventHandler(ABC):
    _events: defaultdict[str, list[Callable]]
    _threaded_events: defaultdict[str, list[Callable]]

    def __init__(self):
        self._thread = None
        self.running = False
        self._events = defaultdict(list)
        self._threaded_events = defaultdict(list)

    def start(self, *, thread=True, ignore_exceptions=True):
        """
        Starts the event handler.

        Keyword Arguments:
            thread (bool): Whether the event handler should be run in a thread.
            ignore_exceptions (bool): Whether to catch exceptions that happen in individual events
        """
        if self.running is False:
            self.ignore_exceptions = ignore_exceptions
            self.running = True
            if thread:
                self._thread = Thread(target=self._updater, args=())
                self._thread.start()
            else:
                self._thread = None
                self._updater()
    
    def call_event(self, event_name, args=[]):
        try:
            if event_name in self._threaded_events:
                for func in self._threaded_events[event_name]:
                    Thread(target=func, args=args).start()
            if event_name in self._events:
                for func in self._events[event_name]:
                    func(*args)
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
    def _updater(self):
        pass

    def stop(self):
        """
        Permanently stops the event handler.
        """
        self.running = False
        if self._thread is not None:
            self._thread = None

    def pause(self):
        """
        Pauses the event handler.
        """
        self.running = False

    def resume(self):
        """
        Resumes the event handler.
        """
        if self.running is False:
            self.start()

    def event(self, function=None, *, thread=False):
        """
        Decorator function. Adds an event.
        """
        def inner(function):
            # called directly if the decorator provides arguments
            if thread is True:
                self._threaded_events[function.__name__].append(function)
            else:
                self._events[function.__name__].append(function)

        if function is None:
            # => the decorator provides arguments
            return inner
        else:
            # => the decorator doesn't provide arguments
            inner(function)