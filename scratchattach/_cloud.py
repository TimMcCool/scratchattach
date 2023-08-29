#----- Cloud interactions
import websocket
import json
import requests
from threading import Thread
import time
from . import _exceptions
import traceback
import warnings

class _CloudMixin:

    def __init__(self, *, project_id, username="python", session_id=None, cloud_host=None, _allow_non_numeric=False, _ws_timeout=None):
        self._session_id = session_id
        self._username = username
        try:
            self.project_id = int(project_id)
        except ValueError: #non-numeric project id (possible on turbowarp's cloud server)
            self.project_id = str(project_id)
        self._ratelimited_until = 0 #deals with the 0.1 second rate limit for cloud variable sets
        self._connect_timestamp = 0 #timestamp of when the cloud connection was opened
        self._ws_timeout = _ws_timeout
        self.websocket = websocket.WebSocket()
        self._connect(cloud_host=cloud_host)
        self._handshake()
        self.cloud_host = cloud_host
        self.allow_non_numeric = _allow_non_numeric #TurboWarp only. If this is true, turbowarp cloud variables can be set to non-numeric values (if) the cloud_host wss allows it)

    def _send_packet(self, packet):
        self.websocket.send(json.dumps(packet) + "\n")

    def disconnect(self):
        self.websocket.close()

    def _handshake(self):
        try:
            self._send_packet(
                {"method": "handshake", "user": self._username, "project_id": self.project_id}
            )
        except Exception:
            self._connect(cloud_host=self.cloud_host)
            self._handshake()

    # ---

    def get_cloud(self):
        # DEPRECATED: On Scratch's cloud variables, this method of getting a cloud variable does not work. On TurboWarp's cloud variables it does work, but there's the scratchattach.get_tw_cloud function for that now
        print("Warning: scratchattach.CloudConnection.get_cloud and scratchattach.TwCloudConnection.get_cloud are deprecated. Use scratchattach.get_cloud or scratchattach.get_tw_cloud instead")
        warnings.warn(
            "scratchattach.CloudConnection.get_cloud and scratchattach.TwCloudConnection.get_cloud are deprecated. Use scratchattach.get_cloud or scratchattach.get_tw_cloud instead", DeprecationWarning
        )
        return []

    def get_var(self, variable):
        # DEPRECATED: On Scratch's cloud variables, this method of getting a cloud variable does not work. On TurboWarp's cloud variables it does work, but there's the scratchattach.get_tw_var function for that now
        print("Warning: scratchattach.CloudConnection.get_var and scratchattach.TwCloudConnection.get_var are deprecated. Use scratchattach.get_var or scratchattach.get_tw_var instead")
        warnings.warn(
            "scratchattach.CloudConnection.get_var and scratchattach.TwCloudConnection.get_var are deprecated. Use scratchattach.get_var or scratchattach.get_tw_var instead", DeprecationWarning
        )
        return None

class CloudConnection(_CloudMixin):

    def _connect(self, *, cloud_host):
        try:
            self.websocket = websocket.WebSocket()
            self.websocket.connect(
                "wss://clouddata.scratch.mit.edu",
                cookie="scratchsessionsid=" + self._session_id + ";",
                origin="https://scratch.mit.edu",
                enable_multithread=True,
                timeout=self._ws_timeout
            )
        except Exception:
            try:
                self.websocket = websocket.WebSocket()
                self.websocket.connect(
                    "wss://clouddata.scratch.mit.edu",
                    cookie="scratchsessionsid=" + self._session_id + ";",
                    origin="https://scratch.mit.edu",
                    enable_multithread=True,
                    timeout=self._ws_timeout
                )
            except Exception:
                raise(_exceptions.ConnectionError)
        self._connect_timestamp = time.time()

    def set_var(self, variable, value):
        variable = variable.replace("☁ ", "")
        if not (value is True or value is False or value in [float('inf'), -float('inf')]):
            value = str(value)
            if len(value) > 256:
                warnings.warn("invalid cloud var (too long): "+str(value), Warning)
                raise(_exceptions.InvalidCloudValue)
            x = value.replace(".", "")
            x = x.replace("-", "")
            if not x.isnumeric():
                warnings.warn("invalid cloud var (not numeric): "+str(value), Warning)
                raise(_exceptions.InvalidCloudValue)
        while self._ratelimited_until + 0.1 >= time.time():
            pass
        try:
            self._send_packet(
                {
                    "method": "set",
                    "name": "☁ " + variable,
                    "value": value,
                    "user": self._username,
                    "project_id": self.project_id,
                }
            )
        except Exception as e:
            try:
                self._handshake()
            except Exception:
                try:
                    self._connect(cloud_host=self.cloud_host)
                    self._handshake()
                except Exception as e:
                    raise _exceptions.ConnectionError("Connection lost while setting cloud variable.", str(e))

            time.sleep(0.1)
            self.set_var(variable, value)
        self._ratelimited_until = time.time()

class TwCloudConnection(_CloudMixin):

    def _connect(self, *, cloud_host, timeout=None):
        try:
            if cloud_host is None:
                cloud_host = "wss://clouddata.turbowarp.org/"
                self.cloud_host = "wss://clouddata.turbowarp.org/"
            self.websocket.connect(
                cloud_host,
                enable_multithread=True,
                timeout = self._ws_timeout
            )
        except Exception:
            raise(_exceptions.ConnectionError)
        self._connect_timestamp = time.time()


    def set_var(self, variable, value):
        variable = variable.replace("☁ ", "")
        if not (value is True or value is False or value in [float('inf'), -float('inf')]):
            value = str(value)
            x = value.replace(".", "")
            x = x.replace("-", "")
            if not x.isnumeric():
                if self.allow_non_numeric is False:
                    raise(_exceptions.InvalidCloudValue)

        while self._ratelimited_until + 0.005 > time.time():
            pass
        try:
            self._send_packet(
                {
                    "method": "set",
                    "name": "☁ " + variable,
                    "value": value,
                    "user": self._username,
                    "project_id": self.project_id,
                }
            )
        except Exception as e:
            try:
                self._handshake()
                time.sleep(0.1)
                self.set_var(variable, value)
            except Exception:
                try:
                    self._connect(cloud_host=None)
                    self._handshake()
                except Exception as e:
                    raise _exceptions.ConnectionError("Connection lost while setting cloud variable.", str(e))

            time.sleep(0.1)
            self.set_var(variable, value)
        self._ratelimited_until = time.time()


class CloudEvents:

    class Event:
        def __init__(self, **entries):
            self.__dict__.update(entries)

    def __init__(self, project_id, **entries):
        self.project_id = int(project_id)
        self.data = get_cloud_logs(project_id=self.project_id, limit = 15)
        self._thread = None
        self.running = False
        self._events = {}
        self.cloud_log_limit = 15
        self.__dict__.update(entries)

    def start(self, *, update_interval = 0.1, thread=True, daemon=False):
        if self.running is False:
            self.update_interval = update_interval
            self.running = True
            if "on_ready" in self._events:
                self._events["on_ready"]()
            if thread:
                self._thread = Thread(target=self._update, args=())
                self._thread.daemon = daemon
                self._thread.start()
            else:
                self._thread = None
                self._update()

    def _update(self):
        while True:
            if self.running:
                data = get_cloud_logs(project_id = self.project_id, limit = self.cloud_log_limit)
                if data != self.data:
                    for activity in data:
                        if activity in self.data:
                            break
                        if "on_"+activity["verb"][:-4] in self._events:
                            try:
                                self._events["on_"+activity["verb"][:-4]](self.Event(user=activity["user"], var=activity["name"][2:], name=activity["name"][2:], value=activity["value"], timestamp=activity["timestamp"]))
                            except Exception as e:
                                print("Warning: Caught error in cloud event - Full error below")
                                try:
                                    traceback.print_exc()
                                except Exception:
                                    print(e)
                self.data = data
            else:
                return
            time.sleep(self.update_interval)

    def stop(self):
        if self._thread is not None:
            self.running = False
            self.project_id = None
            self._thread.join()
            self._thread = None

    def pause(self):
        self.running = False

    def resume(self):
        if self.running is False:
            self.start(update_interval=self.update_interval, thread=True)

    def event(self, function):
        self._events[function.__name__] = function

class TwCloudEvents(CloudEvents):

    def __init__(self, project_id, **entries):
        cloud_connection = TwCloudConnection(project_id=project_id)
        self.data = []
        self._thread = None
        self.running = False
        self._events = {}
        self.connection = cloud_connection
        self.__dict__.update(entries)

    def _update(self):
        while True:
            try:
                data = self.connection.websocket.recv().split('\n')
                result = []
                for i in data:
                    try:
                        result.append(json.loads(i))
                    except Exception: pass
                for activity in result:
                    if "on_"+activity["method"] in self._events:
                        self._events["on_"+activity["method"]](self.Event(user=None, var=activity["name"][2:], name=activity["name"][2:], value=activity["value"], timestamp=time.time()*10000))
            except Exception:
                try:
                    self.connection._connect(cloud_host=self.connection.cloud_host)
                    self.connection._handshake()
                except Exception:
                    if "on_disconnect" in self._events:
                        self._events["on_disconnect"]()

class WsCloudEvents(CloudEvents):

    def __init__(self, project_id, connection, **entries):
        self.data = []
        self._thread = None
        self.running = False
        self._events = {}
        self.connection = connection
        self.__dict__.update(entries)

    def _update(self):
        if isinstance(self.connection, CloudConnection):
            log_data = get_cloud(project_id = self.connection.project_id)
        else:
            log_data = {}
        while True:
            try:
                data = self.connection.websocket.recv().split('\n')
                result = []
                for i in data:
                    try:
                        result.append(json.loads(i))
                    except Exception:
                        pass
                for activity in result:
                    if "on_"+activity["method"] in self._events:
                        if log_data[activity["name"][2:]] == activity["value"]:
                            log_data.pop(activity["name"][2:])
                        else:
                            self._events["on_"+activity["method"]](self.Event(user=None, var=activity["name"][2:], name=activity["name"][2:], value=activity["value"], timestamp=time.time()*10000))
            except Exception:
                try:
                    self.connection._connect(cloud_host=self.connection.cloud_host)
                    self.connection._handshake()
                    if isinstance(self.connection, CloudConnection):
                        log_data = get_cloud(project_id = self.connection.project_id)
                    else:
                        log_data = {}
                except Exception:
                    if "on_disconnect" in self._events:
                        self._events["on_disconnect"]()
# -----


def get_cloud(project_id):
    #Gets the Scratch clouddata of a project from the Scratch cloud log
    try:
        response = json.loads(requests.get(f"https://clouddata.scratch.mit.edu/logs?projectid={project_id}&limit=100&offset=0").text)
        response.reverse()
        clouddata = {}
        for activity in response:
            clouddata[activity["name"][2:]] = activity["value"]
        return clouddata
    except Exception:
        return []

def get_var(project_id, variable):
    #Gets the value of a Scratch cloud variable from the Scratch cloud log
    try:
        response = json.loads(requests.get(f"https://clouddata.scratch.mit.edu/logs?projectid={project_id}&limit=100&offset=0").text)
        response = list(filter(lambda k: k["name"] == "☁ "+variable, response))
        if response == []:
            return None
        else:
            return response[0]["value"]
    except Exception:
        return None

def get_tw_cloud(project_id):
    #Gets the clouddata of a TurboWarp project from the TurboWarp websocket
    #Do not spam this method, it creates a new connection to the TW cloud on every run
    try:
        conn = TwCloudConnection(project_id=project_id, _ws_timeout=1)
        data = conn.websocket.recv().split("\n")
        conn.disconnect()

        result = []
        for i in data:
            try:
                result.append(json.loads(i))
            except Exception: pass
        return result
    except websocket._exceptions.WebSocketTimeoutException:
        return []
    except Exception:
        raise _exceptions.FetchError

def get_tw_var(project_id, variable):
    #Gets the value of a Turbowarp cloud variable from the TW websocket
    #Do not spam this method, it creates a new connection to the TW cloud on every run
    try:
        variable = "☁ " + str(variable)
        result = get_tw_cloud(project_id)
        if result == []:
            return None
        else:
            for i in result:
                if i['name'] == variable:
                    return i['value']
            else:
                return None
    except Exception as e:
        raise _exceptions.FetchError

def get_cloud_logs(project_id, *, filter_by_var_named =None, limit=25, offset=0, log_url="https://clouddata.scratch.mit.edu/logs"):
    try:
        response = json.loads(requests.get(f"{log_url}?projectid={project_id}&limit={limit}&offset={offset}").text)
        if filter_by_var_named is None: return response
        else:
            return list(filter(lambda k: k["name"] == "☁ "+filter_by_var_named, response))
    except Exception:
        return []

def connect_tw_cloud(project_id_arg=None, *, project_id=None):
    if project_id is None:
        project_id = project_id_arg
    if project_id is None:
        return None

    return TwCloudConnection(project_id = int(project_id))
