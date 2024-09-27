from abc import ABC, abstractmethod

import websocket
import json
import time
from ..utils import exceptions
import warnings

class BaseCloud(ABC):

    """
    Base class for a project's cloud variables.

    When inheriting from this class, the __init__ function ...
    - must first call super().__init__()
    - must then set some attributes

    Attributs that must be specified in the __init__ function a class inheriting from this one:
    
    :self._session: Either None or a Session object

    :self.project_id: Project id of the cloud variables

    :self.cloud_host: URL of the websocket server ("wss://..." or "ws://...")

    Attributes that can, but don't have to be specified in the __init__ function:

    :self.ws_ratelimit: The wait time between cloud variable sets. Defaults to 0.1

    :self.allow_non_numeric: Whether non-numeric cloud variable values are allowed. Defaults to False

    :self.length_limit: Length limit for cloud variable values. Defaults to 100000

    :self.header: The header to send. Defaults to None
    
    :self.cookie: The cookie to send. Defaults to None 

    :self.origin: The origin to send. Defaults to None

    :self.print_connect_messages: Whether to print a message on every connect to the cloud server. Defaults to False.
    """

    def __init__(self):
        
        # Internal attributes
        self._ratelimited_until = 0
        self.active_connection = False #whether a connection to a cloud variable server is currently established
        self.websocket = websocket.WebSocket()
        self.recorder = None # A CloudRecorder object that records cloud activity for the values to be retrieved later will be saved in this attribute as soon as .get_var is called

        # Default values for cloud-specific attributes
        self.ws_ratelimit = 0.1
        self.ws_timeout = 3 # Timeout for send operations (after the timeout, the connection will be renewed and the operation will be retried 3 times)
        self.allow_non_numeric = False
        self.length_limit = 100000
        self.header = None
        self.cookie = None
        self.origin = None

    def _assert_auth(self):
        if self._session is None:
            raise exceptions.Unauthenticated(
                "You need to use session.connect_cloud (NOT get_cloud) in order to perform this operation.")

    def send_packet(self, packet):
        self.websocket.send(json.dumps(packet) + "\n")

    def connect(self):
        self.websocket = websocket.WebSocket()
        self.websocket.connect(
            self.cloud_host,
            cookie=self.cookie,
            origin=self.origin,
            enable_multithread=True,
            timeout = self.ws_timeout,
            header = self.header
        )
        if self.print_connect_message:
            print("Connected to cloud server ", self.cloud_host)

    def handshake(self):
        packet = {"method": "handshake", "user": self._session.username, "project_id": self.project_id}
        try:
            self.send_packet(packet)
        except Exception:
            self.connect()
            try:
                self.send_packet(packet)
            except Exception:
                self.connect()
                try:
                    self.send_packet(packet)
                except Exception:
                    raise exceptions.ConnectionError("Handshake failed three times in a row")

    def set_var(self, variable, value):
        """
        Sets a cloud variable.

        Args:
            variable (str): The name of the cloud variable that should be set (provided without the cloud emoji)
            value (str): The value the cloud variable should be set to
        """
        if self.active_connection:
            variable = variable.replace("☁ ", "")
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
            while self._ratelimited_until + 0.1 >= time.time():
                time.sleep(0.001)
            packet = {
                "method": "set",
                "name": "☁ " + variable,
                "value": value,
                "user": self._username,
                "project_id": self.project_id,
            }
            try:
                self.send_packet(packet)
            except Exception:
                self.connect()
                try:
                    self.send_packet(packet)
                except Exception:
                    self.connect()
                    try:
                        self.send_packet(packet)
                    except Exception:
                        raise exceptions.ConnectionError(f"Setting cloud variable {variable} failed three times in a row")
            self._ratelimited_until = time.time()
        else:
            print("Warning: The cloud variable can't be set because there is no active connection.\nCall cloud.connect() before setting the cloud var.") 


        