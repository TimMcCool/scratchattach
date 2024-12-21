from __future__ import annotations

from abc import ABC, abstractmethod
from ..utils.requests import Requests as requests
from threading import Thread
from ..utils import exceptions
import traceback
from . import cloud_recorder

class BaseEventHandler(ABC):

    def __init__(self):
        self._thread = None
        self.running = False
        self._events = {}
        self._threaded_events = {}

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
                Thread(target=self._threaded_events[event_name], args=args).start()
            if event_name in self._events:
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
                self._threaded_events[function.__name__] = function
            else:
                self._events[function.__name__] = function

        if function is None:
            # => the decorator provides arguments
            return inner
        else:
            # => the decorator doesn't provide arguments
            inner(function)