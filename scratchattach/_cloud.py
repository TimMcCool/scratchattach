#----- Cloud interactions
from numpy import var
import websocket
import json
import requests
from threading import Thread
import time
from . import _exceptions
import traceback

class _CloudMixin:

    def __init__(self, *, project_id, username="python", session_id=None, cloud_host=None, _allow_non_numeric=False, _no_reconnect=False):
        self._session_id = session_id
        self._username = username
        try:
            self.project_id = int(project_id)
        except ValueError: #non-numeric project id (possible on turbowarp's cloud server)
            self.project_id = str(project_id)
        self._ratelimited_until = 0#deals with the 0.1 second rate limit for cloud variable sets
        self.websocket = websocket.WebSocket()
        self._no_reconnect = False
        self._connect(cloud_host=cloud_host)
        self._handshake()
        self._no_reconnect = _no_reconnect
        self.cloud_host = cloud_host
        self.allow_non_numeric = _allow_non_numeric #TurboWarp only. If this is true, turbowarp cloud variables can be set to non-numeric values (if) the cloud_host wss allows it)
        self._clouddata = []

    def _send_packet(self, packet):
        self.websocket.send(json.dumps(packet) + "\n")

    def disconnect(self):
        self.websocket.close()

    def _handshake(self):
        if self._no_reconnect is True:
            return
        try:
            self._send_packet(
                {"method": "handshake", "user": self._username, "project_id": self.project_id}
            )
        except Exception:
            self._connect(cloud_host=self.cloud_host)
            self._handshake()

    def get_var(self, variable):
        try:
            variable = "☁ " + str(variable)
            self.set_var('@scratchattach','0')

            result = []
            for i in self._clouddata:
                try:
                    result.append(json.loads(i))
                except Exception: pass
            if result == []:
                return None
            else:
                for i in result:
                    if i['name'] == variable:
                        return i['value']
                return None
        except Exception as e:
            raise _exceptions.FetchError

class CloudConnection(_CloudMixin):

    def _connect(self, *, cloud_host):
        try:
            self.websocket = websocket.WebSocket()
            self.websocket.connect(
                "wss://clouddata.scratch.mit.edu",
                cookie="scratchsessionsid=" + self._session_id + ";",
                origin="https://scratch.mit.edu",
                enable_multithread=True,
            )
        except Exception:
            raise(_exceptions.ConnectionError)

    def set_var(self, variable, value):
        variable = variable.replace("☁ ", "")
        value = str(value)
        if len(value) > 256:
            print("invalid cloud var (too long):", value)
            raise(_exceptions.InvalidCloudValue)
        x = value.replace(".", "")
        x = x.replace("-", "")
        if not x.isnumeric():
            print("invalid cloud var (not numeric):", value)
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
            if variable == "@scratchattach":
                self._clouddata = self.websocket.recv().split('\n')
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

    def _connect(self, *, cloud_host):
        if self._no_reconnect is True:
            return
        try:
            if cloud_host is None:
                cloud_host = "wss://clouddata.turbowarp.org/"
                self.cloud_host = "wss://clouddata.turbowarp.org/"
            self.websocket.connect(
                cloud_host,
                enable_multithread=True
            )
        except Exception:
            raise(_exceptions.ConnectionError)

    def get_cloud(self, variable):
        try:
            variable = "☁ " + str(variable)
            self.set_var('@scratchattach','0')

            result = []
            for i in self._clouddata:
                try:
                    result.append(json.loads(i))
                except Exception: pass
            data = {}
            if result == []:
                return {}
            else:
                for item in result:
                    data[item["name"]] = item["value"]
                return data
        except Exception as e:
            raise _exceptions.FetchError


    def set_var(self, variable, value):
        variable = variable.replace("☁ ", "")
        value = str(value)
        x = value.replace(".", "")
        x = x.replace("-", "")
        if not x.isnumeric():
            if self.allow_non_numeric is False:
                raise(_exceptions.InvalidCloudValue)

        while self._ratelimited_until + 0.1 > time.time():
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
            if variable == "@scratchattach":
                self._clouddata = self.websocket.recv().split('\n') + self._clouddata
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

    def __init__(self, project_id):
        self.project_id = int(project_id)
        self.data = get_cloud_logs(project_id=self.project_id, limit = 15)
        self._thread = None
        self.running = False
        self._events = {}

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
                data = get_cloud_logs(project_id = self.project_id, limit = 15)
                if data != self.data:
                    for activity in data:
                        if activity in self.data:
                            break
                        if "on_"+activity["verb"][:-4] in self._events:
                            try:
                                self._events["on_"+activity["verb"][:-4]](self.Event(user=activity["user"], var=activity["name"][2:], name=activity["name"][2:], value=activity["value"], timestamp=activity["timestamp"]))
                            except Exception as e:
                                print("Caught error in cloud event - Full error below")
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

    def __init__(self, project_id):
        cloud_connection = TwCloudConnection(project_id=project_id)
        self.data = []
        self._thread = None
        self.running = False
        self._events = {}
        self.connection = cloud_connection

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

    def __init__(self, project_id, connection):
        self.data = []
        self._thread = None
        self.running = False
        self._events = {}
        self.connection = connection

    def _update(self):
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
                        self._events["on_"+activity["method"]](self.Event(user=None, var=activity["name"][2:], name=activity["name"][2:], value=activity["value"], timestamp=time.time()*10000))
            except Exception:
                try:
                    self.connection._connect(cloud_host=self.connection.cloud_host)
                    self.connection._handshake()
                except Exception:
                    if "on_disconnect" in self._events:
                        self._events["on_disconnect"]()
# -----

def get_cloud(project_id):
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
    try:
        response = json.loads(requests.get(f"https://clouddata.scratch.mit.edu/logs?projectid={project_id}&limit=100&offset=0").text)
        response = list(filter(lambda k: k["name"] == "☁ "+variable, response))
        if response == []:
            return None
        else:
            return response[0]["value"]
    except Exception:
        return None

def get_cloud_logs(project_id, *, filter_by_var_named =None, limit=25, offset=0, log_url="https://clouddata.scratch.mit.edu/logs"):
    try:
        response = json.loads(requests.get(f"{log_url}?projectid={project_id}&limit={limit}&offset={offset}").text)
        if filter_by_var_named is None: return response
        else:
            return list(filter(lambda k: k["name"] == "☁ "+filter_by_var_named, response))
    except Exception:
        return []
