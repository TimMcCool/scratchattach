from __future__ import annotations
from scratchattach.site.typed_dicts import CloudActivityDict

import json
import time
import ssl
import traceback
from typing import Any
from threading import Thread
import warnings

from SimpleWebSocketServer import SimpleSSLWebSocketServer, SimpleWebSocketServer, WebSocket

from scratchattach.utils import exceptions
from scratchattach.site import cloud_activity
from scratchattach.site.user import User
from scratchattach.cloud import BaseCloud, DummyCloud, AnyCloud
from ._base import BaseCloudServer


class TwCloudSocket(WebSocket):
    server: TwCloudServer | TwSSLCloudServer

    def handle_set(self, data: dict[Any, Any]):
        # cloud variable set received
        # check if client handshaked and username is confirmed
        client_info = self.server.tw_clients.get(self.address)
        if client_info is None or not client_info["name_confirmed"]:
            return
        # check if project_id is in whitelisted projects (if there's a list of whitelisted projects)
        if (
            self.server.whitelisted_projects is not None
            and str(data["project_id"]) not in self.server.whitelisted_projects
        ):
            self.close(4002)
            if self.server.log_var_sets:
                print(
                    self.address[0] + ":" + str(self.address[1]),
                    "tried to set a var on non-whitelisted project and was disconnected, project:",
                    data["project_id"],
                    "user:",
                    data["user"],
                )
            return
        # check if value is valid
        if not self.server._check_value(data["value"]):
            if self.server.log_var_sets:
                print(self.address[0] + ":" + str(self.address[1]), "sent an invalid var value")
            return
        # perform cloud var and forward to other players
        if self.server.log_var_sets:
            print(
                self.address[0] + ":" + str(self.address[1]),
                f"set {data['name']} to {data['value']}, project:",
                str(data["project_id"]),
                "user:",
                data["user"],
            )
        self.server.set_var(
            data["project_id"],
            data["name"],
            data["value"],
            user=data["user"],
            skip_broadcast_for=self,
            no_prefix=True,
        )
        send_to_clients: CloudActivityDict = {
            "method": "set",
            "project_id": data["project_id"],
            "name": data["name"],
            "value": data["value"],
            "cloud": self.server.get_project_cloud(data["project_id"]),
        }
        # raise event
        _a = cloud_activity.CloudActivity(username=data["user"], timestamp=time.time() * 1000)
        _a._update_from_dict(send_to_clients)
        self.server.call_event("on_set", [_a, self])

    def _user_existence_check(self, username: str):
        check_error = None
        try:
            exists = User(username=username).does_exist()
        except Exception as e:
            exists = False
            check_error = e
        client_info = self.server.tw_clients.get(self.address)
        if client_info is None or client_info["client"] is not self:
            return  # client disconnected by now
        if exists:
            client_info["name_confirmed"] = True
            self.server.call_event(
                "on_handshake", [client_info["username"], client_info["project_id"], self]
            )
        else:
            if check_error is None:
                print(
                    self.address[0] + ":" + str(self.address[1]),
                    "tried to handshake using a username not existing on Scratch (will be disconnected), user:",
                    username,
                )
            else:
                print(
                    self.address[0] + ":" + str(self.address[1]),
                    "username check failed:",
                    check_error,
                    "\nThe Scratch website is inaccessible or down. Consider disabling username checks by setting allow_nonscratch_names=True so users can still connect.",
                )
            self.close(4002)

    def handle_handshake(self, data: dict[Any, Any]):
        # check if handshake is valid
        if not "user" in data:
            print(
                self.address[0] + ":" + str(self.address[1]),
                "tried to handshake without providing a username",
            )
            self.close(4002)
            return
        if not "project_id" in data:
            print(
                self.address[0] + ":" + str(self.address[1]),
                "tried to handshake without providing a project_id",
            )
            self.close(4002)
            return
        self.server.tw_clients[self.address]["username"] = data["user"]
        self.server.tw_clients[self.address]["project_id"] = data["project_id"]
        # check if project_id is in whitelisted projects (if there's a list of whitelisted projects)
        if self.server.whitelisted_projects is not None:
            if str(data["project_id"]) not in self.server.whitelisted_projects:
                self.close(4002)
                print(
                    self.address[0] + ":" + str(self.address[1]),
                    "tried to handshake on a non-whitelisted project:",
                    data["project_id"],
                    "user:",
                    data["user"],
                )
                return
        # check if username is allowed
        if not self.server.allow_nonscratch_names:
            Thread(target=self._user_existence_check, args=(data["user"],), daemon=True).start()
        else:
            self.server.tw_clients[self.address]["name_confirmed"] = True
        # register handshake in users list (save username and project_id)
        print(
            self.address[0] + ":" + str(self.address[1]),
            "handshaked, project:",
            data["project_id"],
            "user:",
            data["user"],
        )
        # send current cloud variable values to the user who handshaked
        self.sendMessage(
            "\n".join(
                [
                    json.dumps(
                        {
                            "method": "set",
                            "project_id": data["project_id"],
                            "name": varname,
                            "value": self.server.tw_variables[str(data["project_id"])][varname],
                            "server": "scratchattach/3",
                        }
                    )
                    for varname in self.server.get_project_vars(str(data["project_id"]))
                ]
            )
        )
        self.sendMessage("This server uses @TimMcCool's scratchattach v3.")
        # raise event
        if self.server.allow_nonscratch_names:  # if username checks are enabled, the on_handshake event will be raised after the username existence check is completed (in _user_existence_check)
            self.server.call_event("on_handshake", [data["user"], data["project_id"], self])

    def handleMessage(self):
        if not self.server.running:
            return
        try:
            if self.server.check_for_ip_ban(self):
                return

            data = json.loads(self.data)
            # print(data)

            if data["method"] == "set":
                self.handle_set(data)
            elif data["method"] == "handshake":
                self.handle_handshake(data)
            else:
                print(
                    "Error:",
                    self.address[0] + ":" + str(self.address[1]),
                    "sent a message without providing a valid method (set, handshake)",
                )
        except Exception as e:
            print("Internal error in handleMessage:", e, traceback.format_exc())

    def handleConnected(self):
        if not self.server.running:
            return
        try:
            if self.server.check_for_ip_ban(self):
                return

            print(self.address[0] + ":" + str(self.address[1]), "connected")
            self.server.tw_clients[self.address] = {
                "client": self,
                "username": None,
                "project_id": None,
                "name_confirmed": False,
            }
            # raise event
            self.server.call_event("on_connect", [self])
        except Exception as e:
            print("Internal error in handleConntected:", e)

    def handleClose(self):
        client_info = self.server.tw_clients.pop(self.address, None)
        if not self.server.running or client_info is None:
            return
        try:
            self.server.call_event(
                "on_disconnect",
                [client_info["username"], client_info["project_id"], self],
            )
            print(self.address[0] + ":" + str(self.address[1]), "disconnected")
        except Exception as e:
            print("Internal error in handleClose:", e)


class TwCloudServer(BaseCloudServer, SimpleWebSocketServer):
    def __init__(
        self,
        hostname: str,
        *,
        port: int,
        websocketclass: type[WebSocket],
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

        SimpleWebSocketServer.__init__(self, hostname, port=port, websocketclass=websocketclass)

        BaseCloudServer.__init__(
            self,
            hostname=hostname,
            port=port,
            length_limit=length_limit,
            allow_non_numeric=allow_non_numeric,
            whitelisted_projects=whitelisted_projects,
            allow_nonscratch_names=allow_nonscratch_names,
            blocked_ips=blocked_ips,
            sync_players=sync_players,
            log_var_sets=log_var_sets,
        )


class TwSSLCloudServer(BaseCloudServer, SimpleSSLWebSocketServer):
    def __init__(
        self,
        hostname: str,
        *,
        certfile: str | None = None,
        keyfile: str | None = None,
        ssl_version: int = ssl.PROTOCOL_TLSv1_2,
        ssl_context: ssl.SSLContext | None = None,
        port: int,
        websocketclass: type[WebSocket],
        length_limit: int | None = None,
        allow_non_numeric: bool = True,
        whitelisted_projects: list[Any] | None = None,
        allow_nonscratch_names: bool = True,
        blocked_ips: list[str] | None = None,
        sync_players: bool = True,
        log_var_sets: bool = True,
    ):
        SimpleSSLWebSocketServer.__init__(
            self,
            hostname,
            port=port,
            websocketclass=websocketclass,
            certfile=certfile,
            keyfile=keyfile,
            version=ssl_version,
            ssl_context=ssl_context,
        )

        BaseCloudServer.__init__(
            self,
            hostname=hostname,
            port=port,
            length_limit=length_limit,
            allow_non_numeric=allow_non_numeric,
            whitelisted_projects=whitelisted_projects,
            allow_nonscratch_names=allow_nonscratch_names,
            blocked_ips=blocked_ips,
            sync_players=sync_players,
            log_var_sets=log_var_sets,
        )

    def _updater(self):
        try:
            # Function called when .start() is executed (.start is inherited from BaseEventHandler)
            print(f"Serving websocket server: wss://{self.hostname}:{self.port}")
            self.serveforever()
        except Exception as e:
            raise exceptions.WebsocketServerError(str(e))


def init_cloud_server(
    hostname: str = "127.0.0.1",
    port: int = 8080,
    *,
    length_limit: int | None = None,
    allow_non_numeric: bool = True,
    whitelisted_projects: list[Any] | None = None,
    allow_nonscratch_names: bool = True,
    blocked_ips: list[str] | None = None,
    sync_players: bool = True,
    log_var_sets: bool = True,
):
    """
    Inits a websocket server which can be used with TurboWarp's ?cloud_host URL parameter.

    Prints out the websocket address in the console.
    """
    if blocked_ips is None:
        blocked_ips = []

    return TwCloudServer(
        hostname,
        port=port,
        websocketclass=TwCloudSocket,
        length_limit=length_limit,
        allow_non_numeric=allow_non_numeric,
        whitelisted_projects=whitelisted_projects,
        allow_nonscratch_names=allow_nonscratch_names,
        blocked_ips=blocked_ips,
        sync_players=sync_players,
        log_var_sets=log_var_sets,
    )


def init_ssl_cloud_server(
    hostname: str = "127.0.0.1",
    port: int = 8080,
    *,
    certfile: str | None = None,
    keyfile: str | None = None,
    ssl_version: int = ssl.PROTOCOL_TLSv1_2,
    ssl_context: ssl.SSLContext | None = None,
    length_limit: int | None = None,
    allow_non_numeric: bool = True,
    whitelisted_projects: list[Any] | None = None,
    allow_nonscratch_names: bool = True,
    blocked_ips: list[str] | None = None,
    sync_players: bool = True,
    log_var_sets: bool = True,
) -> TwSSLCloudServer:
    """
    Inits a websocket server which can be used with TurboWarp's ?cloud_host URL parameter.

    Prints out the websocket address in the console.
    """
    if (certfile is None or keyfile is None) and ssl_context is None:
        warnings.warn(
            "To init a ssl cloud server, you need provide `certfile` and "
            + "`keyfile` or `ssl_context`."
        )

    return TwSSLCloudServer(
        hostname,
        port=port,
        websocketclass=TwCloudSocket,
        certfile=certfile,
        keyfile=keyfile,
        ssl_version=ssl_version,
        ssl_context=ssl_context,
        length_limit=length_limit,
        allow_non_numeric=allow_non_numeric,
        whitelisted_projects=whitelisted_projects,
        allow_nonscratch_names=allow_nonscratch_names,
        blocked_ips=blocked_ips,
        sync_players=sync_players,
        log_var_sets=log_var_sets,
    )
