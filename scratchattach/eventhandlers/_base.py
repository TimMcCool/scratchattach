from __future__ import annotations

import json
import time
import ssl
from abc import ABC, abstractmethod
from typing import Optional, Any
from collections import defaultdict
from threading import Thread, Event
from collections.abc import Callable
import traceback
from SimpleWebSocketServer import WebSocket
from rich import print

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

class BaseCloudServer(BaseEventHandler):
    hostname: str
    port: int
    tw_clients: dict[tuple[str, int], dict[str, Any]]
    tw_variables: dict[str, dict[str, Any]]
    allow_non_numeric: bool
    whitelisted_projects: Optional[list[str]]
    length_limit: Optional[int]
    allow_nonscratch_names: bool
    blocked_ips: list[str]
    sync_players: bool
    log_var_sets: bool

    def __init__(self,
                hostname: str,
                *,
                certfile: str|None = None,
                keyfile: str|None = None,
                ssl_version: int = ssl.PROTOCOL_TLSv1_2,
                ssl_context: ssl.SSLContext|None = None,
                port: int,
                websocketclass: type[WebSocket],
                length_limit: int|None = None,
                allow_non_numeric: bool = True,
                whitelisted_projects: list[Any]|None = None,
                allow_nonscratch_names: bool = True,
                blocked_ips: list[str]|None = None,
                sync_players: bool = True,
                log_var_sets: bool = True):

        if blocked_ips is None:
            blocked_ips = []

        BaseEventHandler.__init__(self)

        self.running = False
        self._events = {}  # saves event functions called on cloud updates

        self.tw_clients = {}  # saves connected clients
        self.tw_variables = {}  # holds cloud variable states

        self.hostname = hostname
        self.port = port

        # server config
        self.allow_non_numeric = allow_non_numeric
        self.whitelisted_projects = whitelisted_projects
        self.length_limit = length_limit
        self.allow_nonscratch_names = allow_nonscratch_names
        self.blocked_ips = blocked_ips
        self.sync_players = sync_players
        self.log_var_sets = log_var_sets

    def check_for_ip_ban(self, client):
        if (
            client.address[0] in self.blocked_ips
            or client.address[0] + ":" + str(client.address[1]) in self.blocked_ips
            or client.address in self.blocked_ips
        ):
            client.sendMessage("You have been banned from this server")
            client.close(4002)
            print(f"[yellow]Client {client.address[0]}:{client.address[1]} was forced disconnected "+
                  "due to IP ban. [b]If this dosen't look right, remove them from the list.[/][/]")
            return True
        return False

    def active_projects(self):
        only_active = {}
        for project_id in self.tw_variables:
            if self.active_user_ips(project_id) != []:
                only_active[project_id] = self.tw_variables[project_id]
        return only_active

    def active_user_names(self, project_id):
        return [self.tw_clients[user]["username"] for user in self.active_user_ips(project_id)]

    def active_user_ips(self, project_id):
        return list(filter(lambda user: str(self.tw_clients[user]["project_id"]) == str(project_id), self.tw_clients))

    def get_global_vars(self):
        return self.tw_variables

    def get_project_vars(self, project_id):
        project_id = str(project_id)
        if project_id in self.tw_variables:
            return self.tw_variables[project_id]
        else:
            return {}

    def get_var(self, project_id, var_name):
        project_id = str(project_id)
        var_name = var_name.replace("☁ ", "")
        if project_id in self.tw_variables:
            if var_name in self.tw_variables[project_id]:
                return self.tw_variables[project_id][var_name]
            else:
                print(f"[yellow]Warning: Could not find variable {var_name} in project {project_id}![/]")
                return None
        else:
            print(f"[yellow]Warning: Could not find project {project_id}! Are you sure it exists from the server's perspective? Is it whitelisted?[/]")
            return None

    def set_global_vars(self, data):
        try:
            for project_id in data:
                self.set_project_vars(project_id, data[project_id])
        except Exception as e: # TODO: determine which exception we want to catch specifically
            print(f"[red]Internal Error in BaseCloudServer.set_global_vars:[/]", traceback.format_exc())

    def set_project_vars(self, project_id, data, *, user="@server"):
        project_id = str(project_id)
        self.tw_variables[project_id] = data
        for client in (self.tw_clients[ip]["client"] for ip in self.active_user_ips(project_id)):
            try:
                client.sendMessage(
                    "\n".join(
                        [
                            json.dumps(
                                {
                                    "method": "set",
                                    "project_id": project_id,
                                    "name": "☁ " + varname,
                                    "value": data[varname],
                                    "server": "scratchattach/2.0.0",
                                    "timestamp": time.time() * 1000,
                                    "user": user,
                                }
                            )
                            for varname in data
                        ]
                    )
                )
            except Exception as e: # TODO: determine which exceptions we want to catch specifically
                print(f"[red]Internal Error in BaseCloudServer.set_project_vars:[/]", traceback.format_exc())

    def set_var(self, project_id, var_name, value, *, user="@server", skip_forward=None):
        var_name = var_name.replace("☁ ", "")
        project_id = str(project_id)
        if project_id not in self.tw_variables:
            self.tw_variables[project_id] = {}
        self.tw_variables[project_id][var_name] = value

        if self.sync_players is True:
            for client in (self.tw_clients[ip]["client"] for ip in self.active_user_ips(project_id)):
                if client == skip_forward:
                    continue
                try:
                    client.sendMessage(
                        json.dumps(
                            {
                                "method": "set",
                                "project_id": project_id,
                                "name": "☁ " + var_name,
                                "value": value,
                                "timestamp": time.time() * 1000,
                                "user": user,
                            }
                        )
                    )
                except Exception as e: # TODO: determine which exceptions we want to catch specifically
                    print(f"[red]Internal Error in BaseCloudServer.set_var:[/]", traceback.format_exc())

    def _check_value(self, value):
        # Checks if a received cloud value satisfies the server's constraints
        if self.length_limit is not None:
            if len(str(value)) > self.length_limit:
                return False
        if self.allow_non_numeric is False:
            x = value.replace(".", "")
            x = x.replace("-", "")
            if not (x.isnumeric() or x == ""):
                return False
        return True

    def _updater(self):
        try:
            # Function called when .start() is executed (.start is inherited from BaseEventHandler)
            print(f"Serving websocket server: ws://{self.hostname}:{self.port}")
            self.serveforever()
        except Exception as e:
            raise exceptions.WebsocketServerError(str(e))

    def pause(self):
        self.running = False

    def resume(self):
        self.running = True

    def stop(self, wait_call_threads: bool = True):
        try:
            BaseEventHandler.stop(self, wait_call_threads)
            self.close()
        except Exception as e:
            print(f"[red]Error while stopping cloud server: [/]", traceback.format_exc())
