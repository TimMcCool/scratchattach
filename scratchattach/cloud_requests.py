#----- The cloud request handler class
from . import cloud
import time
from .encoder import *
import math
from threading import Thread
import json
import traceback
import warnings
from . import exceptions

class CloudRequests:
    """
    Framework (inspired by discord.py) that allows Scratch cloud variables and Python to communicate. More information: https://github.com/TimMcCool/scratchattach/wiki/Cloud-Requests
    """
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
        self.respond_in_thread = False
        self.current_var = 0
        self.idle_since = 0
        self.force_reconnect = False

    def __init__(self,
                 cloud_connection: cloud.CloudConnection,
                 *,
                 used_cloud_vars=["1", "2", "3", "4", "5", "6", "7", "8", "9"],
                 ignore_exceptions=True,
                 _force_reconnect = False, # this argument is no longer used and only exists for backwards compatibility
                 _log_url="https://clouddata.scratch.mit.edu/logs",
                 _packet_length=245,
                 **kwargs
                 ):
        print(
            "\033[1mIf you use CloudRequests in your Scratch project, please credit TimMcCool!\033[0m"
        )
        if _log_url != "https://clouddata.scratch.mit.edu/logs":
            warnings.warn(
                "Log URL isn't the URL of Scratch's clouddata logs. Don't use the _log_url parameter unless you know what you are doing",
                RuntimeWarning)
        if _packet_length > 245:
            warnings.warn(
                "The packet length was set to a value higher than default (245). Your project most likely won't work on Scratch.",
                RuntimeWarning)

        self.used_cloud_vars = used_cloud_vars
        self.connection = cloud_connection
        self.project_id = cloud_connection.project_id

        self.ignore_exceptions = ignore_exceptions
        self.log_url = _log_url
        self.packet_length = _packet_length

        self.init_attributes()

    def request(self, function=None, *, enabled=True, name=None, thread=False):
        """
        Decorator function. Adds a request to the request handler.
        """
        def inner(function):
            # called if the decorator provides arguments
            if thread:
                self.respond_in_thread = True
            self.requests[function.__name__ if name is None else name] = {
                "name": function.__name__ if name is None else name,
                "enabled": enabled,
                "on_call": function,
                "thread": thread
            }

        if function is None:
            # => the decorator provides arguments
            return inner
        else:
            # => the decorator doesn't provide arguments
            self.requests[function.__name__] = {
                "name": function.__name__,
                "enabled": True,
                "on_call": function,
                "thread": False
            }

    def call_request(self, request_id, req_obj, arguments):
        """
        Calls a request. Called by the request handler when it detects a request. If the request should be run in a thread, this function is called in a thread.
        """
        request = req_obj["name"]
        try:
            if not req_obj["enabled"]: # Checks if the request is disabled
                print(
                    f"Warning: Client received the disabled request '{request}'"
                )
                self.call_event("on_disabled_request", [
                    self.Request(name=request,
                                 request=request,
                                 requester=self.last_requester,
                                 timestamp=self.last_timestamp,
                                 arguments=arguments,
                                 request_id=request_id)
                ]) # If the request is disabled, the event is called
                return None
            output = req_obj["on_call"](*arguments) # Calls the request function and saves the function's returned data in the output variable
            
            if req_obj["thread"]:
                # If this function is running in a thread, the output is saved in the self.outputs list and parsed by the main request handler
                self.outputs[request_id] = {
                    "output": output,
                    "request": req_obj
                }
            else:
                # If this function is not running in a thread, the output is returned directly 
                self._parse_output(output, request, req_obj, request_id)
        except Exception as e:
            # Handles errors: Calls the on_error event, prints the traceback and sends back the error message to the Scratch project
            self.call_event("on_error", [
                self.Request(name=request,
                             request=request,
                             requester=self.last_requester,
                             timestamp=self.last_timestamp,
                             arguments=arguments,
                             request_id=request_id), e
            ])
            if self.ignore_exceptions:
                print(
                    f"Warning: Caught error in request '{request}' - Full error below"
                )
                try:
                    traceback.print_exc()
                except Exception:
                    print(e)
            else:
                print(f"Warning: Exception in request '{request}':")
                raise (e)
            if req_obj["thread"]:
                self.outputs[request_id] = {
                    "output": f"Error: Check the Python console",
                    "request": req_obj
                }
            else:
                self._parse_output("Error: Check the Python console", request,
                                   req_obj, request_id)

    def add_request(self, function, *, enabled=True, name=None):
        self.request(enabled=enabled, name=name)(function)

    def remove_request(self, name):
        self.requests.pop(name)

    def edit_request(self,
                     name,
                     *,
                     enabled=None,
                     new_name=None,
                     new_function=None,
                     thread=None):
        """
        Edits an existing request.
        
        Args:
            name (str): Current name of the request that should be edited
        
        Keyword Arguments (optional):
            enabled (boolean): Whether the request should be set as enabled
            new_name (str): New name that should be given to the request
            new_function (Callable): Function that should be called when the request is received
            thread (boolean): Whether the request should be run in a thread
        """
        if name not in self.requests:
            raise (exceptions.RequestNotFound(name))
        if enabled is not None:
            self.requests[name]["enabled"] = enabled
        if new_name is not None:
            self.requests[name]["name"] = new_name
        if new_function is not None:
            self.requests[name]["on_call"] = new_function
        if thread is not None:
            self.requests[name]["thread"] = thread

    def event(self, function):
        """
        Decorator function. Adds an event to the request handler.
        """
        self.events.append(function)

    def get_requester(self):
        """
        Can be used inside a request to get the username that performed the request.
        """

        if self.last_requester is None:
            logs = cloud.get_cloud_logs(self.project_id,
                                         filter_by_var_named="TO_HOST")
            activity = list(
                filter(lambda x: "." + self.last_request_id in x["value"],
                       logs))
            if len(activity) > 0:
                self.last_requester = activity[0]["user"]

        return self.last_requester

    def get_timestamp(self):
        """
        Can be used inside a request to get the timestamp of when the request was performed or received.
        """

        return self.last_timestamp

    def get_exact_timestamp(self):
        """
        Can be used inside a request to get the exact timestamp of when the request was performed.
        """
        logs = cloud.get_cloud_logs(self.project_id,
                                     filter_by_var_named="TO_HOST")
        activity = list(
            filter(lambda x: "." + self.last_request_id in x["value"],
                   logs))
        if len(activity) > 0:
            return activity[0]["timestamp"]
        else:
            return None

    def _respond(self, request_id, response, limit, *, validation=2222):
        """
        Sends back the request response to the Scratch project
        """

        if self.idle_since + 8 < time.time() or self.force_reconnect:
            self.connection._connect(cloud_host=self.connection.cloud_host)
            self.connection._handshake()

        remaining_response = str(response)

        i = 0
        while not remaining_response == "":
            if len(remaining_response) > limit:
                response_part = remaining_response[:limit]
                remaining_response = remaining_response[limit:]

                i += 1
                if i > 99:
                    iteration_string = str(i)
                elif i > 9:
                    iteration_string = "0" + str(i)
                else:
                    iteration_string = "00" + str(i)

                try:
                    self.connection.set_var(
                        f"FROM_HOST_{self.used_cloud_vars[self.current_var]}",
                        f"{response_part}.{request_id}{iteration_string}1")
                except Exception:
                    self.call_event("on_disconnect")
                self.current_var += 1
                if self.current_var == len(self.used_cloud_vars):
                    self.current_var = 0
                time.sleep(0.1)
            else:
                try:
                    self.connection.set_var(
                        f"FROM_HOST_{self.used_cloud_vars[self.current_var]}",
                        f"{remaining_response}.{request_id}{validation}")
                except Exception:
                    self.call_event("on_disconnect")
                self.current_var += 1
                if self.current_var == len(self.used_cloud_vars):
                    self.current_var = 0

                remaining_response = ""
                time.sleep(0.1)

        self.idle_since = time.time()

    def run(self,
            thread=False,
            data_from_websocket=True,
            no_packet_loss=False):
        '''
        Starts the request handler.
        
        Args:
            thread: Whether the request handler should be run in a thread.
            data_from_websocket: Whether the websocket should be used to detect requests.
            no_packet_loss: Whether the request handler should reconnect to the cloud websocket before responding to a request, this can help to avoid packet loss.
        '''

        self.force_reconnect = no_packet_loss
        if data_from_websocket is True:
            events = [
                cloud.WsCloudEvents(
                    self.project_id,
                    cloud.CloudConnection(
                        project_id=self.project_id,
                        username=self.connection._username,
                        session_id=self.connection._session_id),
                    update_interval=0),
                cloud.CloudEvents(self.project_id,
                                   update_interval=4.5,
                                   cloud_log_limit=25)
            ]
        else:
            events = []
        if thread:
            thread = Thread(
                target=self._run,
                args=[events],
                kwargs={"data_from_websocket": data_from_websocket})
            thread.start()
        else:
            self._run(events, data_from_websocket=data_from_websocket)

    def call_event(self, event, args=[]):
        """
        Calls an event. Called by the request handler when it detects an event.
        
        
        Returns:
            boolean: True if the called event is defined, else False
        """
        events = list(filter(lambda k: k.__name__ == event, self.events))
        if events == []:
            return False
        else:
            events[0](*args)
            return True

    def _parse_output(self, output, request, req_obj, request_id):
        """
        Prepares the transmission of the request output to the Scratch project
        """
        if len(str(output)) > 3000:
            print(
                f"Warning: Output of request '{request}' is longer than 3000 characters (length: {len(str(output))} characters). Responding the request will take >4 seconds."
            )

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
            self._respond(request_id,
                          output,
                          self.packet_length,
                          validation=3222)
        else:
            self._respond(request_id, output, self.packet_length)

    def _run(self, events, data_from_websocket=True):
        self.ws_data = []
    	
        # Prepares the cloud events:

        def on_set(event):
            if event.name == "TO_HOST":
                self.ws_data.append(event)

        try:
            self.connection._connect(cloud_host=self.connection.cloud_host)
            self.connection._handshake()
        except Exception:
            self.call_event("on_disconnect")

        self.idle_since = time.time()
        self.responded_request_ids = []

        if self.requests == []:
            warnings.warn("You haven't added any requests!", RuntimeWarning)

        while events != []:
            event_handler = events.pop()
            event_handler.event(on_set)
            event_handler.start(update_interval=event_handler.update_interval,
                                thread=True)

        old_clouddata = []
        self.call_event("on_ready")  #Calls the on_ready event

        if data_from_websocket is False:
            # If the data shouldn't be fetched from the cloud websocket, it prepares the cloud log events
            old_clouddata = cloud.get_cloud_logs(self.project_id, filter_by_var_named="TO_HOST", limit=100)
            try:
                self.last_timestamp = old_clouddata[0]["timestamp"]
            except Exception:
                self.last_timestamp = 0

        while True:

            time.sleep(0.001)

            if data_from_websocket is False:
                # If the data shouldn't be fetched from the cloud websocket, it fetches the cloud logs to get data
                clouddata = cloud.get_cloud_logs(
                    self.project_id, filter_by_var_named="TO_HOST", limit=100)
                if clouddata == old_clouddata:
                    continue
                else:
                    old_clouddata = list(clouddata)
                self.ws_data = []
                for activity in clouddata:
                    if activity["timestamp"] > self.last_timestamp:
                        self.ws_data.insert(0,cloud.CloudEvents.Event(user=activity["user"],
                                                 var=activity["name"][2:],
                                                 name=activity["name"][2:],
                                                 value=activity["value"],
                                                 timestamp=activity["timestamp"]))

            current_ws_data = list(self.ws_data)
            self.ws_data = []
            while current_ws_data != []:
                event = current_ws_data.pop(0)

                try:
                    # Parsing the received requests
                    raw_request, request_id = event.value.split(".")

                    if event.value[0] == "-":
                        # => The received request is actually part of a bigger request
                        if not request_id in self.request_parts:
                            self.request_parts[request_id] = []
                        self.request_parts[request_id].append(raw_request[1:])
                        continue # If the end of the request was not received yet, continue with the next received request

                    if request_id in self.responded_request_ids:
                        # Detecting if a request with the same id was parsed before to prevent double responses
                        continue
                    else:
                        self.responded_request_ids.insert(0, request_id)
                        self.responded_request_ids = self.responded_request_ids[:15]
                except Exception:
                    continue

                self.last_requester = event.user
                self.last_timestamp = event.timestamp

                # If the request consists of multiple parts: Putting together the parts to get the whole raw request string
                _raw_request = ""
                if request_id in self.request_parts:
                    data = self.request_parts[request_id]
                    for i in data:
                        _raw_request += i
                    self.request_parts.pop(request_id)
                raw_request = _raw_request + raw_request

                # Decode request and parse arguemtns:
                request = Encoding.decode(raw_request)
                arguments = request.split("&")
                request = arguments.pop(0)

                # Call on_request event:
                self.call_event("on_request", [
                    self.Request(name=request,
                                 request=request,
                                 requester=self.last_requester,
                                 timestamp=self.last_timestamp,
                                 arguments=arguments,
                                 request_id=request_id,
                                 id=request_id)
                ])
                output = "" # initialize the output variable

                # Check if the request is unknown:
                if request not in self.requests:
                    print(
                        f"Warning: Client received an unknown request called '{request}'"
                    )
                    self.call_event("on_unknown_request", [
                        self.Request(name=request,
                                     request=request,
                                     requester=self.last_requester,
                                     timestamp=self.last_timestamp,
                                     arguments=arguments,
                                     request_id=request_id)
                    ])
                    continue
                else:
                    # If the request is not unknown, it is called
                    req_obj = self.requests[request]
                    self.last_request_id = request_id
                    if req_obj["thread"]:
                        # => Call request in a thread
                        Thread(target=self.call_request,
                               args=(request_id, req_obj, arguments)).start()
                    else:
                        # => Call request directly
                        self.call_request(request_id, req_obj, arguments)

            #Send outputs from request that were run in threads and still need to be returned
            # There's still room for improvement here: While the requests that were run in threads are returned or non-threaded requests are running, no new threaded requests will be run. Will be improved in a future scratchattach version.
            while len(list(self.outputs.keys())) > 0:
                output_ids = list(self.outputs.keys())
                for request_id in output_ids:
                    output = self.outputs[request_id]["output"]
                    request = self.outputs[request_id]["request"]["name"]
                    req_obj = self.outputs[request_id]["request"]
                    self._parse_output(output, request, req_obj, request_id)
                    self.outputs.pop(request_id)

class TwCloudRequests(CloudRequests):
    """
    Framework (inspired by discord.py) that allows TurboWarp cloud variables and Python to communicate. More information: https://github.com/TimMcCool/scratchattach/wiki/Cloud-Requests
    """
    def __init__(self,
                 cloud_connection,
                 *,
                 used_cloud_vars=["1", "2", "3", "4", "5", "6", "7", "8", "9"],
                 ignore_exceptions=True,
                 _force_reconnect = False, # this argument is no longer used and only exists for backwards compatibility
                 _packet_length=98800):
        print(
            "\033[1mIf you use CloudRequests in your Scratch project, please credit TimMcCool!\033[0m"
        )
        if _packet_length > 98800:
            warnings.warn(
                "The packet length was set to a value higher than TurboWarp's default (98800).",
                RuntimeWarning)
        self.used_cloud_vars = used_cloud_vars
        self.connection = cloud_connection
        self.project_id = cloud_connection.project_id

        self.ignore_exceptions = ignore_exceptions
        self.packet_length = _packet_length

        self.init_attributes()

    def get_requester(self):
        return None

    def run(self,
            thread=False,
            data_from_websocket=True,
            no_packet_loss=False):
        '''
        Starts the request handler.
        
        Args:
            thread: Whether the request handler should be run in a thread.
            data_from_websocket: Whether the websocket should be used to detect requests.
            no_packet_loss: Whether the request handler should reconnect to the cloud websocket before responding to a request, this can help to avoid packet loss.
        '''
        self.force_reconnect = no_packet_loss
        events = [cloud.TwCloudEvents(self.project_id, update_interval=0)]
        if thread:
            thread = Thread(target=self._run, args=[events])
            thread.start()
        else:
            self._run(events)
