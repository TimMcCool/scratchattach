#----- The cloud request handler class
from . import _cloud
import time
from ._encoder import *
import math
from threading import Thread
import json
import traceback

class CloudRequests:

    class Request:
        def __init__(self, **entries):
            self.__dict__.update(entries)
            self.id = self.request_id

    def __init__(self, cloud_connection : _cloud.CloudConnection, *, used_cloud_vars = ["1","2","3","4","5","6","7","8","9"], ignore_exceptions=True, force_reconnect=True, _log_url="https://clouddata.scratch.mit.edu/logs", _packet_length=220):
        print("\033[1mIf you use CloudRequests in your Scratch project, please credit TimMcCool!\033[0m")
        if _log_url != "https://clouddata.scratch.mit.edu/logs":
            print("Warning: Log URL isn't the URL of Scratch's clouddata logs. Don't use the _log_url parameter unless you know what you are doing.")
        if _packet_length > 220:
            print("Warning: The packet length was set to a value higher than default (220). Your project most likely won't work on Scratch.")
        self.used_cloud_vars = used_cloud_vars
        self.connection = cloud_connection
        self.project_id = cloud_connection.project_id
        self.requests = []
        self.current_var = 0
        self.ignore_exceptions = ignore_exceptions
        self.idle_since = 0
        self.log_url = _log_url
        self.packet_length = _packet_length
        self.last_requester = None
        self.last_timestamp = 0
        self.events = []

    def request(self, function):

        self.requests.append(function)

    def event(self, function):

        self.events.append(function)

    def get_requester(self):

        return self.last_requester

    def get_timestamp(self):

        return self.last_timestamp

    def _respond(self, request_id, response, limit, *, force_reconnect=False):

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

                self.connection.set_var(f"FROM_HOST_{self.used_cloud_vars[self.current_var]}", f"{response_part}.{request_id}{iteration_string}1")
                self.current_var += 1
                if self.current_var == len(self.used_cloud_vars):
                    self.current_var = 0
                time.sleep(0.1)
            else:
                self.connection.set_var(f"FROM_HOST_{self.used_cloud_vars[self.current_var]}", f"{remaining_response}.{request_id}2222")
                self.current_var += 1
                if self.current_var == len(self.used_cloud_vars):
                    self.current_var = 0

                remaining_response = ""
                time.sleep(0.1)

        self.idle_since = time.time()


    def run(self, thread=False, data_from_websocket=False):
        if data_from_websocket is True:
            events = _cloud.WsCloudEvents(self.project_id, _cloud.CloudConnection(project_id = self.project_id, username = self.connection._username, session_id=self.connection._session_id))
        else:
            events = None
        if thread:
            thread = Thread(target=self._run, args=[events], kwargs={"data_from_websocket":data_from_websocket})
            thread.start()
        else:
            self._run(events, data_from_websocket=data_from_websocket)

    def call_event(self, event, args=[]):
        events = list(filter(lambda k: k.__name__ == event, self.events))
        if events == []:
            return False
        else:
            events[0](*args)
            return True

    def _run(self, events, data_from_websocket=False):
        if data_from_websocket:
            self.ws_data = []

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

        self.call_event("on_ready")

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
                        self.last_requester = activity["user"]
                        self.last_timestamp = activity['timestamp']
                        try:
                            raw_request, request_id = activity["value"].split(".")
                        except Exception:
                            self.last_timestamp = activity['timestamp']
                            continue
                        request = Encoding.decode(raw_request)
                        arguments = request.split("&")
                        request = arguments.pop(0)
                        self.call_event("on_request", [self.Request(name=request,request=request,requester=self.last_requester,timestamp=self.last_timestamp,arguments=arguments,request_id=request_id,id=request_id)])
                        output = ""

                        commands = list(filter(lambda k: k.__name__ == request, self.requests))
                        if len(commands) == 0:
                            print(f"Warning: Client received an unknown request called '{request}'")
                            self.call_event("on_unknown_request", [self.Request(name=request,request=request,requester=self.last_requester,timestamp=self.last_timestamp,arguments=arguments,request_id=request_id)])
                            self._respond(request_id, Encoding.encode(f"Error: Unknown request"), self.packet_length)
                        else:
                            try:
                                output = commands[0](*arguments)
                            except Exception as e:
                                self._respond(request_id, Encoding.encode(f"Error: Check the Python console"), self.packet_length)
                                self.call_event("on_error", [self.Request(name=request,request=request,requester=self.last_requester,timestamp=self.last_timestamp,arguments=arguments,request_id=request_id), e])
                                if self.ignore_exceptions:
                                    print(f"Caught error in request '{request}' - Full error below")
                                    try:
                                        traceback.print_exception(e)
                                    except Exception:
                                        print(e)
                                else:
                                    print(f"Exception in request '{request}':")
                                    raise(e)

                        if len(str(output)) > 3000 and not data_from_websocket:
                            print(f"Warning: Output of request '{request}' is longer than 3000 characters (length: {len(str(output))} characters). Responding the request will take >4 seconds.")

                        if output is None:
                            print(f"Warning: Request '{request}' didn't return anything.")
                            self.last_data = data
                            continue
                        elif not isinstance(output, list):
                            if output == "":
                                output = "-"
                            output = Encoding.encode(output)
                        else:
                            input = output
                            output = ""
                            for i in input:
                                output += Encoding.encode(i)
                                output += "89"
                        self._respond(request_id, output, self.packet_length)

                self.last_data = data

class TwCloudRequests(CloudRequests):

    def __init__(self, cloud_connection, *, used_cloud_vars = ["1","2","3","4","5","6","7","8","9"], ignore_exceptions=True, force_reconnect=True, _packet_length=49980):
        print("\033[1mIf you use CloudRequests in your Scratch project, please credit TimMcCool!\033[0m")
        if _packet_length > 49980:
            print("Warning: The packet length was set to a value higher than TurboWarp's default (49980).")
        self.used_cloud_vars = used_cloud_vars
        self.connection = cloud_connection
        self.project_id = cloud_connection.project_id
        self.requests = []
        self.current_var = 1
        self.ignore_exceptions = ignore_exceptions
        self.idle_since = 0
        self.packet_length = _packet_length
        self.last_timestamp = 0
        self.events = []

    def get_requester(self):
        return None

    def run(self, thread=False, data_from_websocket=True):
        events = _cloud.TwCloudEvents(self.project_id)
        if thread:
            thread = Thread(target=self._run, args=[events], kwargs={"data_from_websocket":True})
            thread.start()
        else:
            self._run(events, data_from_websocket=True)
