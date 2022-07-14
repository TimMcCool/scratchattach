#----- The cloud request handler class
from . import _cloud
import time
from ._encoder import *
import math
from threading import Thread
import json

class CloudRequests:

    def __init__(self, cloud_connection : _cloud.CloudConnection, *, ignore_exceptions=True, force_reconnect=True, _log_url="https://clouddata.scratch.mit.edu/logs", _packet_length=220):
        print("\033[1mIf you use CloudRequests in your Scratch project, please credit TimMcCool!\033[0m")
        if _log_url != "https://clouddata.scratch.mit.edu/logs":
            print("Warning: Log URL isn't the URL of Scratch's clouddata logs. Don't use the _log_url parameter unless you know what you are doing.")
        if _packet_length > 220:
            print("Warning: The packet length was set to a value higher than default (220). Your project most likely won't work on Scratch.")
        self.connection = cloud_connection
        self.project_id = cloud_connection.project_id
        self.requests = []
        self.current_var = 1
        self.ignore_exceptions = ignore_exceptions
        self.idle_since = 0
        self.log_url = _log_url
        self.packet_length = _packet_length

    def request(self, function):

        self.requests.append(function)

    def event(self, function):

        if function.__name__ == "on_ready":
            self.on_ready = function

    def _respond(self, request_id, response, limit, *, force_reconnect=False):

        print("respond")

        if self.idle_since + 8 < time.time() or force_reconnect:
            self.connection._connect(cloud_host=self.connection.cloud_host)
            self.connection._handshake()

        remaining_response = str(response)


        i = 0
        while not remaining_response == "":
            if len(remaining_response) > limit:
                response_part = remaining_response[:limit]
                remaining_response = remaining_response[limit:]

                i+=1
                if i > 9:
                    iteration_string = str(i)
                else:
                    iteration_string = "0"+str(i)

                self.connection.set_var(f"FROM_HOST_{self.current_var}", f"{response_part}.{request_id}{iteration_string}1")
                self.current_var += 1
                if self.current_var == 10:
                    self.current_var = 1
                time.sleep(0.1)
            else:
                self.connection.set_var(f"FROM_HOST_{self.current_var}", f"{remaining_response}.{request_id}2222")
                self.current_var += 1
                if self.current_var == 10:
                    self.current_var = 1

                remaining_response = ""
                time.sleep(0.1)

        self.idle_since = time.time()


    def run(self):
        self._run()


    def _run(self, data_from_websocket=False):
        if data_from_websocket:
            self.ws_data = []
            events = _cloud.TwCloudEvents(self.project_id)

            @events.event
            def on_set(event):
                self.ws_data.insert(0, {"user":event.user,"verb":"set_var","name":"☁ "+event.name,"value":event.value,"timestamp":time.time()*10000})
                self.ws_data = self.ws_data[:100]

            events.start()


        self.connection._connect(cloud_host=self.connection.cloud_host)
        self.connection._handshake()
        self.idle_since = time.time()
        if data_from_websocket:
            self.last_data = []
        else:
            self.last_data = _cloud.get_cloud_logs(self.project_id, limit=100, log_url=self.log_url)
        self.last_timestamp = 0

        if not data_from_websocket:
            data = _cloud.get_cloud_logs(self.project_id, limit=100, log_url=self.log_url)
            if data == []:
                pass
            else:
                self.last_timestamp = data[0]["timestamp"]

        try:
            self.on_ready()
        except AttributeError:
            pass

        if self.requests == []:
            print("Warning: You haven't added any requests!")

        while True:

            if data_from_websocket:
                data = self.ws_data
            else:
                data = _cloud.get_cloud_logs(self.project_id, limit=100, log_url=self.log_url)
            if data == []:
                continue
            data.reverse()
            if self.last_data == data:
                if data_from_websocket:
                    pass#time.sleep(0.1)
            else:
                for activity in data:
                    if activity['timestamp'] > self.last_timestamp and activity['name'] == "☁ TO_HOST":
                        try:
                            raw_request, request_id = activity["value"].split(".")
                        except Exception:
                            self.last_timestamp = activity['timestamp']
                            continue
                        request = Encoding.decode(raw_request)
                        arguments = request.split("&")
                        request = arguments.pop(0)
                        output = ""

                        commands = list(filter(lambda k: k.__name__ == request, self.requests))
                        if len(commands) == 0:
                            print(f"Warning: Client received an unknown request called '{request}'")
                            self._respond(request_id, Encoding.encode(f"Error: Unknown request"), self.packet_length)
                        else:
                            try:
                                output = commands[0](*arguments)
                            except TypeError as e:
                                self._respond(request_id, Encoding.encode("Error: Client received too many arguments, not enough arguments or invalid arguments"), self.packet_length)
                                print(f"Error in request '{request}': Client received too many arguments, not enough arguments or invalid arguments.\nOriginal error: {e}")
                            except Exception as e:
                                self._respond(request_id, Encoding.encode(f"Error: Check the Python console"), self.packet_length)
                                if self.ignore_exceptions:
                                    print(f"Caught error in request '{request}': {e}")
                                else:
                                    print(f"Exception in request '{request}':")
                                    raise(e)

                        if len(str(output)) > 3000 and not data_from_websocket:
                            print(f"Warning: Output of request '{request}' is longer than 3000 characters (length: {len(str(output))} characters). Responding the request will take >4 seconds.")

                        if not isinstance(output, list):
                            output = Encoding.encode(output)
                        else:
                            input = output
                            output = ""
                            for i in input:
                                output += Encoding.encode(i)
                                output += "89"
                        self._respond(request_id, output, self.packet_length)
                        self.last_timestamp = activity['timestamp']
                self.last_data = data

class TwCloudRequests(CloudRequests):

    def __init__(self, cloud_connection, *, ignore_exceptions=True, force_reconnect=True, _packet_length=9980):
        print("\033[1mIf you use CloudRequests in your Scratch project, please credit TimMcCool!\033[0m")
        if _packet_length > 9980:
            print("Warning: The packet length was set to a value higher than TurboWarp's default (9980).")
        self.connection = cloud_connection
        self.project_id = cloud_connection.project_id
        self.requests = []
        self.current_var = 1
        self.ignore_exceptions = ignore_exceptions
        self.idle_since = 0
        self.packet_length = _packet_length

    def run(self):
        self._run(data_from_websocket=True)
