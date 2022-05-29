#----- The cloud request handler class
from . import _cloud
import time
from ._encoder import *
import math
from threading import Thread
import json

class CloudRequests:

    def __init__(self, cloud_connection, *, ignore_exceptions=True):
        print("\033[1mIf you use CloudRequests in your Scratch project, please credit TimMcCool!\033[0m")
        self.connection = cloud_connection
        self.project_id = cloud_connection.project_id
        self.requests = []
        self.current_var = 1
        self.ignore_exceptions = ignore_exceptions
        self.idle_since = 0

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
        self.connection._connect(cloud_host=None)
        self.connection._handshake()
        self.idle_since = time.time()
        self.last_data = _cloud.get_cloud_logs(self.project_id, limit=100)
        self.last_timestamp = 0

        data = _cloud.get_cloud_logs(self.project_id, limit=100)
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
            data = _cloud.get_cloud_logs(self.project_id, limit=100)
            if data == []:
                continue
            data.reverse()
            if not self.last_data == data:
                for activity in data:
                    if activity['timestamp'] > self.last_timestamp and activity['name'] == "☁ TO_HOST":
                        raw_request, request_id = activity["value"].split(".")
                        request = Encoding.decode(raw_request)
                        arguments = request.split("&")
                        request = arguments.pop(0)
                        output = ""

                        commands = list(filter(lambda k: k.__name__ == request, self.requests))
                        if len(commands) == 0:
                            print(f"Warning: Client received an unknown request called '{request}'")
                            self._respond(request_id, Encoding.encode(f"Error: Unknown request"), 220)
                        else:
                            try:
                                if len(arguments) == 0:
                                    output = commands[0]()
                                elif len(arguments) == 1:
                                    output = commands[0](arguments[0])
                                elif len(arguments) == 2:
                                    output = commands[0](arguments[0],arguments[1])
                                else:
                                    print(f"Error in request '{request}': Request failed to parse. Don't use the character '&' in your requests.")
                                    output = Encoding.encode("Error: Request failed to parse.")
                            except TypeError as e:
                                self._respond(request_id, Encoding.encode("Error: Client received too many arguments, not enough arguments or invalid arguments"), 220)
                                print(f"Error in request '{request}': Client received too many arguments, not enough arguments or invalid arguments.\nOriginal error: {e}")
                            except Exception as e:
                                self._respond(request_id, Encoding.encode(f"Error: Check the Python console"), 220)
                                if self.ignore_exceptions:
                                    print(f"Caught error in request '{request}': {e}")
                                else:
                                    print(f"Exception in request '{request}':")
                                    raise(e)

                        if len(str(output)) > 3000:
                            print(f"Warning: Output of request '{request}' is longer than 3000 characters (length: {len(str(output))} characters). Responding the request will take >4 seconds.")

                        if not isinstance(output, list):
                            output = Encoding.encode(output)
                        else:
                            input = output
                            output = ""
                            for i in input:
                                output += Encoding.encode(i)
                                output += "89"
                        self._respond(request_id, output, 220)
                        self.last_timestamp = activity['timestamp']
                self.last_data = data

''' not working yet
class TwCloudRequests(CloudRequests):


    def _update(self):
        while True:
            print("hi")
            data = self.connection.websocket.recv().split('\n')
            print(data)
            for i in data:
                try:
                    activity = json.loads(i)
                    if activity['name'] == "☁ TO_HOST":
                        self._cloud_log.insert(0, {"user":"TurboWarp","verb":"set_var","name":activity["name"],"value":activity["value"],"timestamp":time.time()})
                        if len(self._cloud_log) > 100:
                            self._cloud_log = self._cloud_log[:100]
                except Exception as e:
                    print(e)
            print(":", self._cloud_log)

    def run(self):
        self.connection._connect(cloud_host=self.connection.cloud_host)
        self.connection._handshake()

        self.idle_since = time.time()
        self.last_data = []
        self.last_timestamp = 0

        self._cloud_log = []
        self._thread = Thread(target=self._update, args=()).start()

        print(f"A TurboWarp request handler is run. Requests will be received from https://turbowarp.org/{self.connection.project_id}?cloud_host={self.connection.cloud_host}")
        try:
            self.on_ready()
        except AttributeError:
            pass

        if self.requests == []:
            print("Warning: You haven't added any requests!")

        while True:
            data = self._cloud_log
            if data == []:
                continue
            data.reverse()
            if True:
                for activity in data:
                    if activity['timestamp'] > self.last_timestamp:
                        raw_request, request_id = activity["value"].split(".")
                        request = Encoding.decode(raw_request)
                        arguments = request.split("&")
                        request = arguments.pop(0)
                        output = ""

                        commands = list(filter(lambda k: k.__name__ == request, self.requests))
                        if len(commands) == 0:
                            print(f"Warning: Client received an unknown request called '{request}'")
                            self._respond(request_id, Encoding.encode(f"Error: Unknown request"), 49980, force_reconnect=True)
                        else:
                            try:
                                if len(arguments) == 0:
                                    output = commands[0]()
                                elif len(arguments) == 1:
                                    output = commands[0](arguments[0])
                                elif len(arguments) == 2:
                                    output = commands[0](arguments[0],arguments[1])
                                else:
                                    print(f"Error in request '{request}': Request failed to parse. Don't use the character '&' in your requests.")
                                    output = Encoding.encode("Error: Request failed to parse.")
                            except TypeError as e:
                                self._respond(request_id, Encoding.encode("Error: Client received too many arguments, not enough arguments or invalid arguments"), 49980, force_reconnect=True)
                                print(f"Error in request '{request}': Client received too many arguments, not enough arguments or invalid arguments.\nOriginal error: {e}")
                            except Exception as e:
                                self._respond(request_id, Encoding.encode(f"Error: Check the Python console"), 49980, force_reconnect=True)
                                if self.ignore_exceptions:
                                    print(f"Caught error in request '{request}': {e}")
                                else:
                                    print(f"Exception in request '{request}':")
                                    raise(e)

                        if not isinstance(output, list):
                            output = Encoding.encode(output)
                        else:
                            input = output
                            output = ""
                            for i in input:
                                output += Encoding.encode(i)
                                output += "89"
                        self._respond(request_id, output, 49980, force_reconnect=True)
                        self.last_timestamp = activity['timestamp']
                self.last_data = data
'''
