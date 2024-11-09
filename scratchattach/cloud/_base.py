from abc import ABC, abstractmethod

import websocket
import json
import time
from ..utils import exceptions
import warnings
from ..eventhandlers import cloud_recorder
import ssl

class BaseCloud(ABC):

    """
    Base class for a project's cloud variables. Represents a cloud.

    When inheriting from this class, the __init__ function of the inherited class ...

    - must first call the constructor of the super class: super().__init__()

    - must then set some attributes

    Attributes that must be specified in the __init__ function a class inheriting from this one:

    :self.project_id: Project id of the cloud variables

    :self.cloud_host: URL of the websocket server ("wss://..." or "ws://...")

    Attributes that can, but don't have to be specified in the __init__ function:

    :self._session: Either None or a site.session.Session object. Defaults to None.

    :self.ws_shortterm_ratelimit: The wait time between cloud variable sets. Defaults to 0.1

    :self.ws_longterm_ratelimit: The amount of cloud variable set that can be performed long-term without ever getting ratelimited

    :self.allow_non_numeric: Whether non-numeric cloud variable values are allowed. Defaults to False

    :self.length_limit: Length limit for cloud variable values. Defaults to 100000

    :self.username: The username to send during handshake. Defaults to "scratchattach"

    :self.header: The header to send. Defaults to None

    :self.cookie: The cookie to send. Defaults to None

    :self.origin: The origin to send. Defaults to None

    :self.print_connect_messages: Whether to print a message on every connect to the cloud server. Defaults to False.
    """

    def __init__(self):

        # Required internal attributes that every object representing a cloud needs to have (no matter what cloud is represented):
        self._session = None
        self.active_connection = False #whether a connection to a cloud variable server is currently established
        self.websocket = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
        self.recorder = None # A CloudRecorder object that records cloud activity for the values to be retrieved later will be saved in this attribute as soon as .get_var is called
        self.first_var_set = 0
        self.last_var_set = 0
        self.var_stets_since_first = 0

        # Set default values for attributes that save configurations specific to the represented cloud:
        # (These attributes can be specifically in the constructors of classes inheriting from this base class)
        self.ws_shortterm_ratelimit = 0.06667
        self.ws_longterm_ratelimit = 0.1
        self.ws_timeout = 3 # Timeout for send operations (after the timeout, the connection will be renewed and the operation will be retried 3 times)
        self.allow_non_numeric = False
        self.length_limit = 100000
        self.username = "scratchattach"
        self.header = None
        self.cookie = None
        self.origin = None
        self.print_connect_message = False

    def _assert_auth(self):
        if self._session is None:
            raise exceptions.Unauthenticated(
                "You need to use session.connect_cloud (NOT get_cloud) in order to perform this operation.")

    def _send_packet(self, packet):
        try:
            self.websocket.send(json.dumps(packet) + "\n")
        except Exception:
            time.sleep(0.1)
            self.connect()
            time.sleep(0.1)
            try:
                self.websocket.send(json.dumps(packet) + "\n")
            except Exception:
                time.sleep(0.2)
                self.connect()
                time.sleep(0.2)
                try:
                    self.websocket.send(json.dumps(packet) + "\n")
                except Exception:
                    time.sleep(1.6)
                    self.connect()
                    time.sleep(1.4)
                    try:
                        self.websocket.send(json.dumps(packet) + "\n")
                    except Exception:
                        self.active_connection = False
                        raise exceptions.CloudConnectionError(f"Sending packet failed three times in a row: {packet}")

    def _send_packet_list(self, packet_list):
        packet_string = "".join([json.dumps(packet) + "\n" for packet in packet_list])
        try:
            self.websocket.send(packet_string)
        except Exception:
            time.sleep(0.1)
            self.connect()
            time.sleep(0.1)
            try:
                self.websocket.send(packet_string)
            except Exception:
                time.sleep(0.2)
                self.connect()
                time.sleep(0.2)
                try:
                    self.websocket.send(packet_string)
                except Exception:
                    time.sleep(1.6)
                    self.connect()
                    time.sleep(1.4)
                    try:
                        self.websocket.send(packet_string)
                    except Exception:
                        self.active_connection = False
                        raise exceptions.CloudConnectionError(f"Sending packet list failed four times in a row: {packet_list}")

    def _handshake(self):
        packet = {"method": "handshake", "user": self.username, "project_id": self.project_id}
        self._send_packet(packet)

    def connect(self):
        self.websocket = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
        self.websocket.connect(
            self.cloud_host,
            cookie=self.cookie,
            origin=self.origin,
            enable_multithread=True,
            timeout = self.ws_timeout,
            header = self.header
        )
        self._handshake()
        self.active_connection = True
        if self.print_connect_message:
            print("Connected to cloud server ", self.cloud_host)

    def disconnect(self):
        self.active_connection = False
        if self.recorder is not None:
            self.recorder.stop()
            self.recorder.source_cloud.disconnect()
            self.recorder = None
        try:
            self.websocket.close()
        except Exception:
            pass

    def reconnect(self):
        self.disconnect()
        self.connect()

    def _assert_valid_value(self, value):
        if not (value in [True, False, float('inf'), -float('inf')]):
            value = str(value)
            if len(value) > self.length_limit:
                raise(exceptions.InvalidCloudValue(
                    f"Value exceeds length limit: {str(value)}"
                ))
            if not self.allow_non_numeric:
                x = value.replace(".", "")
                x = x.replace("-", "")
                if not (x.isnumeric() or x == ""):
                    raise(exceptions.InvalidCloudValue(
                        "Value not numeric"
                    ))

    def _enforce_ratelimit(self, *, n):
        # n is the amount of variables being set
        if (time.time() - self.first_var_set) / (self.var_stets_since_first+1) > self.ws_longterm_ratelimit: # if the average delay between cloud variable sets has been bigger than the long-term rate-limit, cloud variables can be set fast (wait time smaller than long-term rate limit) again
            self.var_stets_since_first = 0
            self.first_var_set = time.time()

        wait_time = self.ws_shortterm_ratelimit * n
        if time.time() - self.first_var_set > 25: # if cloud variables have been continously set fast (wait time smaller than long-term rate limit) for 25 seconds, they should be set slow now (wait time = long-term rate limit) to avoid getting rate-limited
            wait_time = self.ws_longterm_ratelimit * n
        while self.last_var_set + wait_time >= time.time():
            time.sleep(0.001)
        

    def set_var(self, variable, value):
        """
        Sets a cloud variable.

        Args:
            variable (str): The name of the cloud variable that should be set (provided without the cloud emoji)
            value (str): The value the cloud variable should be set to
        """
        self._assert_valid_value(value)
        if not isinstance(variable, str):
            raise ValueError("cloud var name must be a string")
        if not self.active_connection:
            self.connect()
        self._enforce_ratelimit(n=1)

        self.var_stets_since_first += 1

        packet = {
            "method": "set",
            "name": "☁ " + variable,
            "value": value,
            "user": self.username,
            "project_id": self.project_id,
        }
        self._send_packet(packet)
        self.last_var_set = time.time()

    def set_vars(self, var_value_dict, *, intelligent_waits=True):
        """
        Sets multiple cloud variables at once (works for an unlimited amount of variables).

        Args:
            var_value_dict (dict): variable:value dictionary with the variables / values to set. The dict should like this: {"var1":"value1", "var2":"value2", ...}
        
        Kwargs:
            intelligent_waits (boolean): When enabled, the method will automatically decide how long to wait before performing this cloud variable set, to make sure no rate limits are triggered
        """
        if not self.active_connection:
            self.connect()
        if intelligent_waits:
            self._enforce_ratelimit(n=len(list(var_value_dict.keys())))
            
        self.var_stets_since_first += len(list(var_value_dict.keys()))

        packet_list = []
        for variable in var_value_dict:
            value = var_value_dict[variable]
            self._assert_valid_value(value)
            if not isinstance(variable, str):
                raise ValueError("cloud var name must be a string")
            packet = {
                "method": "set",
                "name": "☁ " + variable,
                "value": value,
                "user": self.username,
                "project_id": self.project_id,
            }
            packet_list.append(packet)
        self._send_packet_list(packet_list)
        self.last_var_set = time.time()

    def get_var(self, var, *, recorder_initial_values={}):
        if self.recorder is None:
            self.recorder = cloud_recorder.CloudRecorder(self, initial_values=recorder_initial_values)
            self.recorder.start()
            start_time = time.time()
            while not (self.recorder.cloud_values != {} or start_time < time.time() -5):
                time.sleep(0.01)
        return self.recorder.get_var(var)

    def get_all_vars(self, *, recorder_initial_values={}):
        if self.recorder is None:
            self.recorder = cloud_recorder.CloudRecorder(self, initial_values=recorder_initial_values)
            self.recorder.start()
            start_time = time.time()
            while not (self.recorder.cloud_values != {} or start_time < time.time() -5):
                time.sleep(0.01)
        return self.recorder.get_all_vars()

    def events(self):
        from ..eventhandlers.cloud_events import CloudEvents
        return CloudEvents(self)

    def requests(self, *, no_packet_loss=False, used_cloud_vars=["1", "2", "3", "4", "5", "6", "7", "8", "9"], respond_order="receive"):
        from ..eventhandlers.cloud_requests import CloudRequests
        return CloudRequests(self, used_cloud_vars=used_cloud_vars, no_packet_loss=no_packet_loss, respond_order=respond_order)

    def storage(self, *, no_packet_loss=False, used_cloud_vars=["1", "2", "3", "4", "5", "6", "7", "8", "9"]):
        from ..eventhandlers.cloud_storage import CloudStorage
        return CloudStorage(self, used_cloud_vars=used_cloud_vars, no_packet_loss=no_packet_loss)
