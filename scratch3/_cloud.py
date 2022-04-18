#----- Cloud interactions

import websocket
import json
import requests
from threading import Thread
import time

class _CloudMixin:

    def __init__(self, *, project_id, username="python", session_id=None, cloud_host=None):
        self._session_id = session_id
        self._username = username
        self.project_id = str(project_id)
        self._ratelimited_until = 0#deals with the 0.1 second rate limit for cloud variable sets
        self._connect(cloud_host=cloud_host)

    def _send_packet(self, packet):
        self.websocket.send(json.dumps(packet) + "\n")

    def disconnect(self):
        self.websocket.close()

    def _handshake(self):
        self._send_packet(
            {"method": "handshake", "user": self._username, "project_id": self.project_id}
        )

class CloudConnection(_CloudMixin):

    def _connect(self, *, cloud_host):
        self.websocket = websocket.WebSocket()
        self.websocket.connect(
            "wss://clouddata.scratch.mit.edu",
            cookie="scratchsessionsid=" + self._session_id + ";",
            origin="https://scratch.mit.edu",
            enable_multithread=True,
        )

    def set_var(self, variable, value):
        while self._ratelimited_until + 0.1 > time.time():
            pass
        try:
            self._send_packet(
                {
                    "method": "set",
                    "name": "☁ " + variable,
                    "value": str(value),
                    "user": self._username,
                    "project_id": self.project_id,
                }
            )
        except Exception as e:
            print(e)
            try:
                self._handshake()
            except Exception:
                self._connect(cloud_host=None)
                self._handshake()

            time.sleep(0.1)
            self.set_var(variable, value)
        self._ratelimited_until = time.time()

class TwCloudConnection(_CloudMixin):

    def _connect(self, *, cloud_host):
        if cloud_host is None:
            cloud_host = "wss://clouddata.turbowarp.org/"
        self.websocket = websocket.WebSocket()
        self.websocket.connect(
            cloud_host,
        )
        self._handshake()


    def set_var(self, variable, value):
        while self._ratelimited_until + 0.1 > time.time():
            pass
        try:
            self._send_packet(
                {
                    "method": "set",
                    "name": "☁ " + variable,
                    "value": str(value),
                    "user": self._username,
                    "project_id": self.project_id,
                }
            )
            self.websocket.recv()
        except Exception as e:
            print(e)
            try:
                self._handshake()
            except Exception:
                self._connect(cloud_host=None)
                self._handshake()

            time.sleep(0.1)
            self.set_var(variable, value)
        self._ratelimited_until = time.time()


class CloudEvents:

    class Event:
        def __init__(self, **entries):
            self.__dict__.update(entries)

    def __init__(self, *, project_id):
        self.project_id = int(project_id)
        self.data = get_cloud_logs(project_id=self.project_id, limit = 15)
        self._thread = None
        self.running = False
        self._events = {}

    def start(self, *, update_interval = 0.1):
        if self.running is False:
            self.update_interval = update_interval
            self.running = True
            self._thread = Thread(target=self._update, args=()).start()
            if "on_ready" in self._events:
                self._events["on_ready"]()

    def _update(self):
        while True:
            if self.running:
                data = get_cloud_logs(project_id = self.project_id, limit = 15)
                if data != self.data:
                    for activity in data:
                        if activity in self.data:
                            break
                        if "on_"+activity["verb"][:-4] in self._events:
                            self._events["on_"+activity["verb"][:-4]](self.Event(user=activity["user"], var=activity["name"][2:], value=activity["value"], timestamp=activity["timestamp"]))
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

    def event(self, function):
        self._events[function.__name__] = function
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
        return []

def get_cloud_logs(project_id, *, filter_by_var_named =None, limit=25, offset=0):
    try:
        response = json.loads(requests.get(f"https://clouddata.scratch.mit.edu/logs?projectid={project_id}&limit={limit}&offset={offset}").text)
        if filter_by_var_named is None: return response
        else:
            return list(filter(lambda k: k["name"] == "☁ "+filter_by_var_named, response))
    except Exception:
        return []
