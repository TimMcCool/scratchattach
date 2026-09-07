from __future__ import annotations

import json
import time
import ssl
from abc import ABC, abstractmethod
from typing import Optional, Any, TYPE_CHECKING
from collections import defaultdict
from threading import Thread, Event
from collections.abc import Callable
import traceback

from SimpleWebSocketServer import WebSocket

if TYPE_CHECKING:
    import scratchattach.cloud._base as cloud_base
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

    def call_event(self, event_name, args: list = []):
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
                print(f"Warning: Caught error in event '{event_name}' - Full error below")
                try:
                    traceback.print_exc()
                except Exception:
                    print(e)
            else:
                raise (e)

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
    """
    Base class for all sa cloud servers.

    If you are developing a custom cloud server with sa, please inherit from this class
    and change up the methods as needed.
    """

    hostname: str
    "IP address or domain name of the host to bind the server to."
    port: int
    "Port to bind the server to."
    tw_clients: dict[tuple[str, int], dict[str, Any]]
    "Dictionary containing information on connected clients."
    tw_variables: dict[str, dict[str, Any]]
    "Dictionary containing states and data for existing cloud variables."
    allow_non_numeric: bool
    "Whether or not non-numeric characters are allowed in cloud variable values."
    whitelisted_projects: set[str] | None
    "Optional list of whitelisted projects."
    length_limit: int | None
    "Optional limit on the length of cloud variable values."
    allow_nonscratch_names: bool
    "Whether or not usernames that do not exist on scratch are allowed."
    blocked_ips: list[str]
    "List of blocked IP addresses."
    sync_players: bool
    log_var_sets: bool
    linked_clouds: dict[str, "cloud_base.CloudServerAdapter"]

    def __init__(
        self,
        hostname: str,
        *,
        port: int,
        length_limit: int | None = None,
        allow_non_numeric: bool = True,
        whitelisted_projects: list[Any] | None = None,
        allow_nonscratch_names: bool = True,
        blocked_ips: list[str] | None = None,
        sync_players: bool = True,
        log_var_sets: bool = True,
    ):

        if blocked_ips is None:
            blocked_ips = []

        BaseEventHandler.__init__(self)

        self.tw_clients = {}  # saves connected clients
        self.tw_variables = {}  # holds cloud variable states

        self.hostname = hostname
        self.port = port

        # server config
        self.allow_non_numeric = allow_non_numeric
        self.whitelisted_projects = (
            {str(i) for i in whitelisted_projects} if whitelisted_projects else None
        )
        self.length_limit = length_limit
        self.allow_nonscratch_names = allow_nonscratch_names
        self.blocked_ips = blocked_ips
        self.sync_players = sync_players
        self.log_var_sets = log_var_sets

        self.linked_clouds = {}

    def check_for_ip_ban(self, client):
        if (
            client.address[0] in self.blocked_ips
            or client.address[0] + ":" + str(client.address[1]) in self.blocked_ips
            or client.address in self.blocked_ips
        ):
            client.sendMessage("You have been banned from this server")
            client.close(4002)
            print(client.address[0] + ":" + str(client.address[1]), "(IP-banned) was disconnected")
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

    def active_user_ips(self, project_id: Any):
        project_id = str(project_id)
        return [
            user
            for user in self.tw_clients
            if str(self.tw_clients[user]["project_id"]) == project_id
        ]

    def get_global_vars(self):
        return self.tw_variables

    def get_project_vars(self, project_id: Any):
        project_id = str(project_id)
        return self.tw_variables.get(project_id, {})

    def get_var(self, project_id: Any, var_name: str, *, no_prefix: bool = False):
        project_id = str(project_id)
        if not no_prefix:
            var_name = "☁ " + var_name.removeprefix("☁ ")
        if project_id in self.tw_variables:
            if var_name in self.tw_variables[project_id]:
                return self.tw_variables[project_id][var_name]
            else:
                return None
        else:
            return None

    def set_global_vars(
        self,
        data: dict[str, dict[str, Any]],
        no_prefix: bool = False,
    ):
        for project_id, project_data in data.items():
            self.set_project_vars(project_id, project_data, no_prefix=no_prefix)

    def set_project_vars(
        self,
        project_id: Any,
        data: dict[str, Any],
        *,
        user: str = "@server",
        no_prefix: bool = False,
    ):
        project_id = str(project_id)
        if not no_prefix:
            data = {"☁ " + key.removeprefix("☁ "): value for key, value in data.items()}
        self.tw_variables[project_id].update(data)
        packets = [
            {
                "method": "set",
                "project_id": project_id,
                "name": varname,
                "value": data[varname],
                "server": "scratchattach/3",
                "timestamp": time.time() * 1000,
                "user": user,
            }
            for varname in data
        ]
        packets_string = "\n".join(json.dumps(packet) for packet in packets)
        for client in (self.tw_clients[ip]["client"] for ip in self.active_user_ips(project_id)):
            client.sendMessage(packets_string)
        for packet in packets:
            self.call_event("outgoing_packet", [packet])

    def set_var(
        self,
        project_id: Any,
        var_name: str,
        value: Any,
        *,
        user: str = "@server",
        skip_broadcast_for: WebSocket | None = None,
        no_prefix: bool = False,
    ):
        if not no_prefix:
            var_name = "☁ " + var_name.removeprefix("☁ ")
        project_id = str(project_id)
        if project_id not in self.tw_variables:
            self.tw_variables[project_id] = {}
        self.tw_variables[project_id][var_name] = value

        packet = {
            "method": "set",
            "project_id": project_id,
            "name": var_name,
            "value": value,
            "server": "scratchattach/3",
            "timestamp": time.time() * 1000,
            "user": user,
        }
        if self.sync_players is True:
            for client in (
                self.tw_clients[ip]["client"] for ip in self.active_user_ips(project_id)
            ):
                if client == skip_broadcast_for:
                    continue
                client.sendMessage(json.dumps(packet))
        self.call_event("outgoing_packet", [packet])

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
            while self.running:
                self.serveonce()
        except Exception as e:
            raise exceptions.WebsocketServerError(str(e))

    def get_project_cloud(self, project_id: Any) -> "cloud_base.CloudServerAdapter":
        project_id = str(project_id)
        if project_id not in self.linked_clouds:
            from scratchattach.cloud import _base as cloud_base
            self.linked_clouds[project_id] = cloud_base.CloudServerAdapter(self, project_id)
        return self.linked_clouds[project_id]

    def pause(self):
        self.running = False

    def resume(self):
        self.running = True

    def stop(self, wait_call_threads: bool = True):
        BaseEventHandler.stop(self, wait_call_threads)
        self.close()
