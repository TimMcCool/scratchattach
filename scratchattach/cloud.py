#----- Cloud interactions
import websocket
import json
import requests
from threading import Thread
import time
from . import exceptions
import traceback
import warnings

class _CloudMixin:
    """
    Base class for a connection to a cloud variable server.
    """

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
    """
    Represents a connection to Scratch's cloud variable server.

    Attributes:

    :.websocket: The websocket connection (WebSocket object from the websocket-client library)
    """

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
                raise(exceptions.ConnectionError)
        self._connect_timestamp = time.time()

    def set_var(self, variable, value):
        """
        Sets a cloud variable.

        Args:
            variable (str): The name of the cloud variable that should be set (provided without the cloud emoji)
            value (str): The value the cloud variable should be set to
        """
        variable = variable.replace("☁ ", "")
        if not (value is True or value is False or value in [float('inf'), -float('inf')]):
            value = str(value)
            if len(value) > 256:
                warnings.warn("invalid cloud var (too long): "+str(value), Warning)
                raise(exceptions.InvalidCloudValue)
            x = value.replace(".", "")
            x = x.replace("-", "")
            if not x.isnumeric():
                warnings.warn("invalid cloud var (not numeric): "+str(value), Warning)
                raise(exceptions.InvalidCloudValue)
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
                    raise exceptions.ConnectionError("Connection lost while setting cloud variable.", str(e))

            time.sleep(0.1)
            self.set_var(variable, value)
        self._ratelimited_until = time.time()

class TwCloudConnection(_CloudMixin):
    """
    Represents a connection to TurboWarp's cloud variable server or a custom cloud variable server that behaves like TurboWarp's.

    Attributes:

    :.websocket: The websocket connection (WebSocket object from the websocket-client library)

    :.cloud_host: The websocket URL of the cloud variable server
    
    :.allow_non_numeric: Whether the cloud variables can be set to non-numeric values
    """

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
            raise(exceptions.ConnectionError)
        self._connect_timestamp = time.time()


    def set_var(self, variable, value):
        """
        Sets a cloud variable.

        Args:
            variable (str): The name of the cloud variable that should be set (provided without the cloud emoji)
            value (str): The value the cloud variable should be set to
        """
        variable = variable.replace("☁ ", "")
        if not (value is True or value is False or value in [float('inf'), -float('inf')]):
            value = str(value)
            x = value.replace(".", "")
            x = x.replace("-", "")
            if not x.isnumeric():
                if self.allow_non_numeric is False:
                    raise(exceptions.InvalidCloudValue)

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
                    raise exceptions.ConnectionError("Connection lost while setting cloud variable.", str(e))

            time.sleep(0.1)
            self.set_var(variable, value)
        self._ratelimited_until = time.time()


class CloudEvents:
    """
    Class that calls events on Scratch cloud variable updates. Data fetched from Scratch's clouddata logs.
    """
    class Event:
        """
        Represents a received cloud event. When the cloud event handler calls a cloud event, an Event object is provided as attribute.

        Attributes:

        .user: The user who caused the cloud event (the user who added / set / deleted the cloud variable)

        .var: The name of the cloud variable that was updated (specified without the cloud emoji)

        .name: The name of the cloud variable that was updated (specified without the cloud emoji)

        .timestamp: Then timestamp of when the action was performed

        .value: If the cloud variable was set, then this attribute provides the value the cloud variable was set to
        """
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

    def start(self, *, update_interval = 0.1, thread=True):
        """
        Starts the cloud event handler.

        Keyword Arguments:
            update_interval (float): The clouddata log is continuosly checked for cloud updates. This argument provides the interval between these checks.
            thread (boolean): Whether the event handler should be run in a thread.
        """
        if self.running is False:
            self.update_interval = update_interval
            self.running = True
            if "on_ready" in self._events:
                self._events["on_ready"]()
            if thread:
                self._thread = Thread(target=self._update, args=())
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
        """
        Permanently stops the cloud event handler.
        """
        if self._thread is not None:
            self.running = False
            self.project_id = None
            self._thread.join()
            self._thread = None

    def pause(self):
        """
        Pauses the cloud event handler.
        """
        self.running = False

    def resume(self):
        """
        Resumes the cloud event handler.
        """
        if self.running is False:
            self.start(update_interval=self.update_interval, thread=True)

    def event(self, function):
        """
        Decorator function. Adds a cloud event.
        """
        self._events[function.__name__] = function

class TwCloudEvents(CloudEvents):
    """
    Class that calls events on TurboWarp cloud variable updates. Data fetched from Turbowarp cloud websocket.
    """
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
    """
    Class that calls events on Scratch or Turbowarp cloud variable updates. Data fetched using the provided CloudConnection or TwCloudConnection object.
    """
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
    """
    Gets the clouddata of a Scratch cloud project.

    Args:
        project_id (str):
    
    Returns:
        dict: The values of the project's cloud variables
    """
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
    """
    Gets the value of of a Scratch cloud variable.
    
    Args:
        project_id (str):
        variable (str): The name of the cloud variable (specified without the cloud emoji)
    
    Returns:
        str: The cloud variable's value
    
    If the value can't be fetched, the method returns None.
    """
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
    """
    Gets the clouddata of a TurboWarp cloud project.

    Warning:
        Do not spam this method, it creates a new connection to the TurboWarp cloud server every time it is called.

    Args:
        project_id (str):
    
    Returns:
        dict: The values of the project's cloud variables
    """

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
        raise exceptions.FetchError

def get_tw_var(project_id, variable):
    """
    Gets the value of of a TurboWarp cloud variable.

    Warning:
        Do not spam this method, it creates a new connection to the TurboWarp cloud server every time it is called.

    Args:
        project_id (str):
        variable (str): The name of the cloud variable (specified without the cloud emoji)
    
    Returns:
        str: The cloud variable's value
    
    If the value can't be fetched, the method returns None.
    """
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
        raise exceptions.FetchError

def get_cloud_logs(project_id, *, filter_by_var_named =None, limit=25, offset=0):
    """
    Gets Scratch's clouddata log for a project.
    
    Args:
        project_id:
    
    Keyword Arguments:
        filter_by_var_named (str or None): If you only want to get data for one cloud variable, set this argument to its name.
        limit (int): Max. amount of returned activity.
        offset (int): Offset of the first activity in the returned list.
        log_url (str): If you want to get the clouddata from a cloud log API different to Scratch's normal cloud log API, set this argument to the URL of the API. Only set this argument if you know what you are doing. If you want to get the clouddata from the normal API, don't put this argument.
    """
    try:
        response = json.loads(requests.get(f"{log_url}?projectid={project_id}&limit={limit}&offset={offset}").text)
        if filter_by_var_named is None: return response
        else:
            return list(filter(lambda k: k["name"] == "☁ "+filter_by_var_named, response))
    except Exception:
        return []

def connect_tw_cloud(project_id_arg=None, *, project_id=None):
    """
    Connects to TurboWarp's cloud websocket.

    Args:
        project_id (str)

    Returns:
        scratchattach.cloud.TwCloudConnection: An object that represents a connection to TurboWarp's cloud server
    """
    if project_id is None:
        project_id = project_id_arg
    if project_id is None:
        return None

    return TwCloudConnection(project_id = int(project_id))
