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

    def init_attributes(self):
        self.last_requester = None
        self.last_timestamp = 0
        self.last_request_id = None

        self.requests = {}
        self.events = []

        self.request_parts = {}
        self.outputs = {}
        self.respond_in_thread= False
        self.current_var = 0
        self.idle_since = 0

    def __init__(self, cloud_connection : _cloud.CloudConnection, *, used_cloud_vars = ["1","2","3","4","5","6","7","8","9"], ignore_exceptions=True, force_reconnect=True, _log_url="https://clouddata.scratch.mit.edu/logs", _packet_length=245):
        print("\033[1mIf you use CloudRequests in your Scratch project, please credit TimMcCool!\033[0m")
        if _log_url != "https://clouddata.scratch.mit.edu/logs":
            print("Warning: Log URL isn't the URL of Scratch's clouddata logs. Don't use the _log_url parameter unless you know what you are doing.")
        if _packet_length > 245:
            print("Warning: The packet length was set to a value higher than default (245). Your project most likely won't work on Scratch.")

        self.used_cloud_vars = used_cloud_vars
        self.connection = cloud_connection
        self.project_id = cloud_connection.project_id

        self.ignore_exceptions = ignore_exceptions
        self.log_url = _log_url
        self.packet_length = _packet_length

        self.init_attributes()

    def request(self, function=None, *, enabled=True, name=None, thread=False):
        def inner(function):
            if thread:
                self.respond_in_thread = True
                print("Warning: Running individual requests in threads increases CPU usage")
            self.requests[function.__name__ if name is None else name] = {"name":function.__name__ if name is None else name,"enabled":enabled,"on_call":function,"thread":thread}
        if function is None:
            return inner
        else:
            self.requests[function.__name__] = {"name":function.__name__,"enabled":True,"on_call":function,"thread":False}

    def call_request(self, request_id, req_obj, arguments):
        request = req_obj["name"]
        try:
            if not req_obj["enabled"]:
                print(f"Warning: Client received the disabled request '{request}'")
                self.call_event("on_disabled_request", [self.Request(name=request,request=request,requester=self.last_requester,timestamp=self.last_timestamp,arguments=arguments,request_id=request_id)])
                return None
            output = req_obj["on_call"](*arguments)
            if req_obj["thread"]:
                self.outputs[request_id] = {"output":output, "request":req_obj}
            else:
                self._parse_output(output, request, req_obj, request_id)
        except Exception as e:
            self.call_event("on_error", [self.Request(name=request,request=request,requester=self.last_requester,timestamp=self.last_timestamp,arguments=arguments,request_id=request_id), e])
            if self.ignore_exceptions:
                print(f"Caught error in request '{request}' - Full error below")
                try:
                    traceback.print_exc()
                except Exception:
                    print(e)
            else:
                print(f"Exception in request '{request}':")
                raise(e)
            if req_obj["thread"]:
                self.outputs[request_id] = {"output":f"Error: Check the Python console", "request":req_obj}
            else:
                self._parse_output("Error: Check the Python console", request, req_obj, request_id)

    def add_request(self, function, *, enabled=True, name=None):
        self.request(enabled=enabled, name=name)(function)

    def remove_request(self, name):
        self.requests.pop(name)

    def edit_request(self, name, *, enabled=None, new_name=None, new_function=None, thread=None):
        if name not in self.requests:
            raise(_exceptions.RequestNotFound(name))
        if enabled is not None:
            self.requests[name]["enabled"] = enabled
        if new_name is not None:
            self.requests[name]["name"] = new_name
        if new_function is not None:
            self.requests[name]["on_call"] = new_function
        if thread is not None:
            self.requests[name]["thread"] = thread

    def event(self, function):

        self.events.append(function)

    def get_requester(self):

        if self.last_requester is None:
            logs = _cloud.get_cloud_logs(self.project_id, filter_by_var_named="TO_HOST")
            activity = list(filter(lambda x : "."+self.last_request_id in x["value"], logs))
            if len(activity) > 0:
                self.last_requester = activity[0]["user"]

        return self.last_requester

    def get_timestamp(self):

        return self.last_timestamp

    def _respond(self, request_id, response, limit, *, force_reconnect=False, validation=2222):

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
                if i > 99:
                    iteration_string = str(i)
                elif i > 9:
                    iteration_string = "0"+str(i)
                else:
                    iteration_string = "00"+str(i)

                try:
                    self.connection.set_var(f"FROM_HOST_{self.used_cloud_vars[self.current_var]}", f"{response_part}.{request_id}{iteration_string}1")
                except Exception:
                    self.call_event("on_disconnect")
                self.current_var += 1
                if self.current_var == len(self.used_cloud_vars):
                    self.current_var = 0
                time.sleep(0.1)
            else:
                try:
                    self.connection.set_var(f"FROM_HOST_{self.used_cloud_vars[self.current_var]}", f"{remaining_response}.{request_id}{validation}")
                except Exception:
                    self.call_event("on_disconnect")
                self.current_var += 1
                if self.current_var == len(self.used_cloud_vars):
                    self.current_var = 0

                remaining_response = ""
                time.sleep(0.1)

        self.idle_since = time.time()

    def run(self, thread=False, data_from_websocket=True):
        if data_from_websocket is True:
            events = _cloud.WsCloudEvents(self.project_id, _cloud.CloudConnection(project_id = self.project_id, username = self.connection._username, session_id=self.connection._session_id))
        else:
            events = _cloud.CloudEvents(self.project_id)
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

    def _parse_output(self, output, request, req_obj, request_id):
        if len(str(output)) > 3000 and not self.data_from_websocket:
            print(f"Warning: Output of request '{request}' is longer than 3000 characters (length: {len(str(output))} characters). Responding the request will take >4 seconds.")

        if str(request_id).endswith("0"):
            try:
                int(output) == output
            except Exception:
                send_as_integer = False
            else:
                send_as_integer = not "-" in str(output)
        else:
            send_as_integer = False


        if output is None:
            print(f"Warning: Request '{request}' didn't return anything.")
            return
        elif send_as_integer:
            output = str(output)
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
        if send_as_integer:
            self._respond(request_id, output, self.packet_length, validation=3222)
        else:
            self._respond(request_id, output, self.packet_length)


    def _run(self, events, data_from_websocket=False):
        self.ws_data = []
        self.data_from_websocket = data_from_websocket

        if data_from_websocket or self.respond_in_thread:
            self.cloud_events = events

            @self.cloud_events.event
            def on_set(event):
                if event.name == "TO_HOST":
                    self.ws_data.insert(0, {"user":event.user,"value":event.value,"timestamp":event.timestamp})
                self.ws_data = self.ws_data[:100]

            @self.cloud_events.event
            def on_disconnect():
                self.call_event("on_disconnect")

            self.cloud_events.start(update_interval=0)
        else:
            self.cloud_events = None


        try:
            self.connection._connect(cloud_host=self.connection.cloud_host)
            self.connection._handshake()
        except Exception:
            self.call_event("on_disconnect")
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

            if data_from_websocket or self.respond_in_thread:
                data = self.ws_data
            else:
                data = _cloud.get_cloud_logs(self.project_id, limit=100, log_url=self.log_url, filter_by_var_named="TO_HOST")
                self.ws_data = data
            if self.ws_data == []:
                continue
            data.reverse()
            if self.last_data == data:
                pass
            else:
                for activity in data:
                    if activity['timestamp'] > self.last_timestamp:
                        self.last_requester = activity["user"]
                        self.last_timestamp = activity['timestamp']

                        try:
                            raw_request, request_id = activity["value"].split(".")
                        except Exception:
                            self.last_timestamp = activity['timestamp']
                            continue


                        if activity["value"][0] == "-":
                            if not request_id in self.request_parts:
                                self.request_parts[request_id] = []
                            self.request_parts[request_id].append(raw_request[1:])
                            continue

                        _raw_request = ""
                        if request_id in self.request_parts:
                            data = self.request_parts[request_id]
                            for i in data:
                                _raw_request += i
                            self.request_parts.pop(request_id)
                        raw_request = _raw_request + raw_request

                        request = Encoding.decode(raw_request)
                        arguments = request.split("&")
                        request = arguments.pop(0)
                        self.call_event("on_request", [self.Request(name=request,request=request,requester=self.last_requester,timestamp=self.last_timestamp,arguments=arguments,request_id=request_id,id=request_id)])
                        output = ""

                        if request not in self.requests:
                            print(f"Warning: Client received an unknown request called '{request}'")
                            self.call_event("on_unknown_request", [self.Request(name=request,request=request,requester=self.last_requester,timestamp=self.last_timestamp,arguments=arguments,request_id=request_id)])
                            continue
                        else:
                            req_obj = self.requests[request]
                            self.last_request_id = request_id
                            if req_obj["thread"]:
                                Thread(target=self.call_request, args=(request_id, req_obj, arguments)).start()
                            else:
                                self.call_request(request_id, req_obj, arguments)
                self.last_data = data

            output_ids = list(self.outputs.keys())
            if len(output_ids) > 0:
                for request_id in output_ids:
                    output = self.outputs[request_id]["output"]
                    request = self.outputs[request_id]["request"]["name"]
                    req_obj = self.outputs[request_id]["request"]
                    self._parse_output(output, request, req_obj, request_id)

class TwCloudRequests(CloudRequests):

    def __init__(self, cloud_connection, *, used_cloud_vars = ["1","2","3","4","5","6","7","8","9"], ignore_exceptions=True, force_reconnect=True, _packet_length=98800):
        print("\033[1mIf you use CloudRequests in your Scratch project, please credit TimMcCool!\033[0m")
        if _packet_length > 98800:
            print("Warning: The packet length was set to a value higher than TurboWarp's default (98800).")
        self.used_cloud_vars = used_cloud_vars
        self.connection = cloud_connection
        self.project_id = cloud_connection.project_id

        self.ignore_exceptions = ignore_exceptions
        self.packet_length = _packet_length

        self.init_attributes()

    def get_requester(self):
        return None

    def run(self, thread=False, data_from_websocket=True):
        events = _cloud.TwCloudEvents(self.project_id)
        if thread:
            thread = Thread(target=self._run, args=[events], kwargs={"data_from_websocket":True})
            thread.start()
        else:
            self._run(events, data_from_websocket=True)
