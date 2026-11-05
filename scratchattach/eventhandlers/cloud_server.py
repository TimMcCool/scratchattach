from __future__ import annotations
import socket

from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from threading import Thread
from scratchattach.utils import exceptions
import json
import time
from scratchattach.site import cloud_activity
from scratchattach.site.user import User
from ._base import BaseEventHandler
import traceback

CLIENT_SEND_QUEUE_LIMIT = 1000  # if a client has more than this many messages in their send queue, disconnect them to prevent lag

class TwCloudSocket(WebSocket):
    server: TwCloudServer

    def handle_set(self, data: dict):
        # cloud variable set received
        # check if client handshaked and username is confirmed
        client_info = self.server.tw_clients.get(self.address)
        if client_info is None or not client_info["name_confirmed"]:
            return
        # check if project_id is in whitelisted projects (if there's a list of whitelisted projects)
        if self.server.whitelisted_projects is not None:
            if data["project_id"] not in self.server.whitelisted_projects:
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
        self.server.set_var(data["project_id"], data["name"], data["value"], user=data["user"], skip_forward=self)
        send_to_clients = {
            "method": "set",
            "user": data["user"],
            "project_id": data["project_id"],
            "name": data["name"],
            "value": data["value"],
            "timestamp": round(time.time() * 1000),
            "server": "scratchattach/2.0.0",
        }
        # raise event
        _a = cloud_activity.CloudActivity(timestamp=time.time() * 1000)
        data["name"] = data["name"].replace("☁ ", "")
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
            self.server.call_event("on_handshake", [client_info["username"], client_info["project_id"], self])
        else:
            if check_error is None:
                print(
                    self.address[0] + ":" + str(self.address[1]),
                    "tried to handshake using a username not existing on Scratch (will be disconnected), user:",
                    username,
                )
            else:
                print(self.address[0] + ":" + str(self.address[1]), "username check failed:", check_error, "\nThe Scratch website is inaccessible or down. Consider disabling username checks by setting allow_nonscratch_names=True so users can still connect.")
            self.close(4002)

    def handle_handshake(self, data: dict):
        # check if handshake is valid
        if not "user" in data:
            print(self.address[0] + ":" + str(self.address[1]), "tried to handshake without providing a username")
            self.close(4002)
            return
        if not "project_id" in data:
            print(self.address[0] + ":" + str(self.address[1]), "tried to handshake without providing a project_id")
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
        # check if project_id is in username is allowed
        if self.server.allow_nonscratch_names is False:
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
                            "name": "☁ " + varname,
                            "value": self.server.tw_variables[str(data["project_id"])][varname],
                            "server": "scratchattach/2.0.0",
                        }
                    )
                    for varname in self.server.get_project_vars(str(data["project_id"]))
                ]
            )
        )
        self.sendMessage("This server uses @TimMcCool's scratchattach 2.0.0")
        # raise event
        if self.server.allow_nonscratch_names: # if username checks are enabled, the on_handshake event will be raised after the username existence check is completed (in _user_existence_check)
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
            self.server.tw_clients[self.address] = {"client": self, "username": None, "project_id": None, "name_confirmed":False}
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

class TwCloudServer(SimpleWebSocketServer, BaseEventHandler):
    def __init__(
        self,
        hostname,
        *,
        port,
        websocketclass,
        length_limit=None,
        allow_non_numeric=True,
        whitelisted_projects=None,
        allow_nonscratch_names=True,
        blocked_ips=None,
        sync_players=True,
        log_var_sets=True,
    ):
        if blocked_ips is None:
            blocked_ips = []

        SimpleWebSocketServer.__init__(self, hostname, port=port, websocketclass=websocketclass)
        BaseEventHandler.__init__(self)

        self.running = False

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
                return None
        else:
            return None

    def set_global_vars(self, data):
        for project_id in data:
            self.set_project_vars(project_id, data[project_id])

    def _distribute_to_clients(self, project_id, json_string, *, skip_forward=None):
        for client in [self.tw_clients[ip]["client"] for ip in self.active_user_ips(project_id)]:
            if client == skip_forward:
                continue
            if len(client.sendq) > CLIENT_SEND_QUEUE_LIMIT: # if the client has a large send queue, disconnect them to prevent lag
                client.sendq.clear()  # free the memory now
                try:
                    client.client.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                continue
            client.sendMessage(json_string)

    def set_project_vars(self, project_id, data, *, user="@server"):
        project_id = str(project_id)
        self.tw_variables[project_id] = data
        json_string = "\n".join(
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
        self._distribute_to_clients(project_id, json_string)

    def set_var(self, project_id, var_name, value, *, user="@server", skip_forward=None):
        var_name = var_name.replace("☁ ", "")
        project_id = str(project_id)
        if project_id not in self.tw_variables:
            self.tw_variables[project_id] = {}
        self.tw_variables[project_id][var_name] = value
        json_string = json.dumps(
            {
                "method": "set",
                "project_id": project_id,
                "name": "☁ " + var_name,
                "value": value,
                "timestamp": time.time() * 1000,
                "user": user,
            }
        )
        if self.sync_players is True:
            self._distribute_to_clients(project_id, json_string, skip_forward=skip_forward)

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
        BaseEventHandler.stop(self, wait_call_threads)
        self.close()


def init_cloud_server(
    hostname="127.0.0.1",
    port=8080,
    *,
    length_limit=None,
    allow_non_numeric=True,
    whitelisted_projects=None,
    allow_nonscratch_names=True,
    blocked_ips=None,
    sync_players=True,
    log_var_sets=True,
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
