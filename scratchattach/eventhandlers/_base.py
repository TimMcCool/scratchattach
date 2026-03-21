from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional
from collections import defaultdict
from threading import Thread, Event
from collections.abc import Callable
import traceback
from scratchattach.utils.requests import requests
from scratchattach.utils import exceptions

class BaseEventHandler(ABC):
    _events: defaultdict[str, list[Callable]]
    _threaded_events: defaultdict[str, list[Callable]]
    running: bool
    _thread: Optional[Thread]
    _call_threads: list[Thread]

    def __init__(self):
        self._thread = None
        self.running = False
        self._call_threads = []
        self._events = defaultdict(list)
        self._threaded_events = defaultdict(list)
        # print(f"{self._threaded_events=}")

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
    
    def call_event(self, event_name, args : list = []):
        try:
            # print(f"Calling for {event_name}...")
            if event_name in self._threaded_events:
                for func in self._threaded_events[event_name]:
                    thread = Thread(target=func, args=args)
                    self._call_threads.append(thread)
                    thread.start()
            if event_name in self._events:
                for func in self._events[event_name]:
                    # print(f"Called {func}.")
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
    
    def __del__(self):
        self.stop()

    def stop(self, wait_call_threads: bool = True):
        """
        Permanently stops the event handler.
        """
        # print("Stopping event handler...")
        self.running = False
        thread = self._thread
        if thread is not None:
            thread.join()
            self._thread = None
        if not wait_call_threads:
            return
        for thread in self._call_threads:
            thread.join()

    def pause(self):
        """
        Pauses the event handler.
        """
        self.running = False
        thread = self._thread
        if thread is not None:
            thread.join()

    def resume(self):
        """
        Resumes the event handler.
        """
        if not self.running:
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