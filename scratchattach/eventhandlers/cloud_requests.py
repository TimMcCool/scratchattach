"""v2 ready: CloudRequests class (threading.Condition version)"""

from .cloud_events import CloudEvents
from ..site import project
from threading import Thread, Condition
import time
import traceback
from ..utils.encoder import Encoding

class Request:

    """
    Saves a request added to the request handler
    """

    def __init__(self, request_name, *, on_call, cloud_requests, thread=True, enabled=True, response_priority=0):
        self.name = request_name
        self.on_call = on_call
        self.thread = thread
        self.enabled = enabled
        self.response_priority = response_priority
        self.cloud_requests = cloud_requests # the corresponding CloudRequests object
        
    def __call__(self, received_request):
        if not self.enabled:
            self.cloud_requests.call_event("on_disabled_request", [received_request])
        try:
            output = self.on_call(*received_request.arguments)
            self.cloud_requests.request_outputs.append({"receive":received_request.timestamp, "request_id":received_request.request_id, "output":output, "priority":self.response_priority})
        except Exception as e:
            Thread(target=self.cloud_requests.call_event, args=["on_error", [received_request, e]]).start()
            if self.cloud_requests.ignore_exceptions:
                print(
                    f"Warning: Caught error in request '{self.name}' - Full error below"
                )
                try:
                    traceback.print_exc()
                except Exception:
                    print(e)
            else:
                print(f"Exception in request '{self.name}':")
                raise(e)
        self.cloud_requests.request_outputs.append({"receive":received_request.timestamp, "request_id":received_request.request_id, "output":[f"Error in request {self.name}","Check the Python console"], "priority":self.response_priority})
        print("about to aquire")
        with self.cloud_requests.responder_condition:
            print("about to notify responder")
            self.cloud_requests.responder_condition.notify() # Activate the .cloud_requests._responder process so it sends back the data to Scratch

class ReceivedRequest:

    def __init__(self, **entries):
        self.__dict__.update(entries)

class CloudRequests(CloudEvents):

    # The CloudRequests class is built upon CloudEvents, similar to how Filterbot is built upon MessageEvents

    def __init__(self, cloud, used_cloud_vars=["1", "2", "3", "4", "5", "6", "7", "8", "9"], no_packet_loss=True):
        super().__init__(cloud)
        # Setup
        self._requests = {}
        self.event(self.on_set)
        self.respond_in_thread = False
        self.no_packet_loss = no_packet_loss # When enabled, query the clouddata log regularly for missed requests and reconnect after every single request (reduces packet loss a lot, but is spammy and can make response duration longer)
        self.used_cloud_vars = used_cloud_vars

        # Lists and dicts for saving request-related stuff
        self.request_parts = {} # Dict (key: request_id) for saving the parts of the requests not fully received yet
        self.received_requests = [] # List saving the requests that have been fully received, but not executed yet (as ReceivedRequest objects). Requests that run in threads will never be put into this list, but are executed directly.
        self.executed_requests = {} # Dict (key: request_id) saving the request that are currently being executed and have not been responded yet (as ReceivedRequest objects)
        self.request_outputs = [] # List for the output data returned by the requests (so the thread sending it back to Scratch can access it)
        self.responded_request_ids = [] # Saves the last 15 request ids that have been responded to. This prevents double responses then using the clouddata logs as 2nd source for preventing packet loss

        # threading Condition objects used to block threads until they are needed (lower CPU usage compared to a busy-sleep event queue)#
        self.executer_condition = Condition()
        self.responder_condition = Condition()

        # Start ._executer and ._responder threads (these threads are remain blocked until cloud activity is received and don't consume any CPU)
        self.executer_thread = Thread(target=self._executer)
        self.responder_thread = Thread(target=self._responder)
        self.executer_thread.start()
        self.responder_thread.start()

        self.current_var = 0 # ID of the last set FROM_HOST_ variable (when a response is sent back to Scratch, these are set cyclically)
        self.credit_check()

    # -- Adding and removing requests --

    def request(self, function=None, *, enabled=True, name=None, thread=False, response_priority=0):
        """
        Decorator function. Adds a request to the request handler.
        """
        def inner(function):
            # called if the decorator provides arguments
            if thread:
                self.respond_in_thread = True
            self._requests[function.__name__ if name is None else name] = Request(
                function.__name__ if name is None else name,
                enabled = enabled,
                thread=thread,
                response_priority=response_priority,
                on_call=function,
                cloud_requests=self
            )

        if function is None:
            # => the decorator provides arguments
            return inner
        else:
            # => the decorator doesn't provide arguments
            self._requests[function.__name__] = Request(
                function.__name__,
                on_call=function,
                cloud_requests=self
            )

    def add_request(self, function, *, enabled=True, name=None):
        self.request(enabled=enabled, name=name)(function)

    def remove_request(self, name):
        self._requests.pop(name)

    # -- Parse and send back the request output --

    def _parse_output(self, received_request, output):
        """
        Prepares the transmission of the request output to the Scratch project
        """
        if len(str(output)) > 3000:
            print(
                f"Warning: Output of request '{received_request.request.name}' is longer than 3000 characters (length: {len(str(output))} characters). Responding the request will take >4 seconds."
            )

        if str(received_request.request_id).endswith("0"):
            try:
                int(output) == output
            except Exception:
                send_as_integer = False
            else:
                send_as_integer = not ("-" in str(output)) and not isinstance(output, bool)
        else:
            send_as_integer = False

        if output is None:
            print(f"Warning: Request '{received_request.request.name}' didn't return anything.")
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
        self._respond(received_request.request_id, output, validation=3222 if send_as_integer else None)

    def _respond(self, request_id, response, *, validation=2222):
        """
        Sends back the request response to the Scratch project
        """

        if (self.cloud.last_var_set + 8 < time.time() # if the cloud connection has been idle for too long, a reconnect is necessary to make sure the first package will not be lost
            ) or self.no_packet_loss:
            self.cloud.reconnect()

        remaining_response = str(response)
        length_limit = self.cloud.length_limit - (len(str(request_id))+6) # the subtrahend is the worst-case length of the "."+numbers after the "."

        i = 0
        while not remaining_response == "":
            if len(remaining_response) > length_limit:
                response_part = remaining_response[:length_limit]
                remaining_response = remaining_response[length_limit:]

                i += 1
                if i > 99:
                    iteration_string = str(i)
                elif i > 9:
                    iteration_string = "0" + str(i)
                else:
                    iteration_string = "00" + str(i)

                try:
                    self.cloud.set_var(
                        f"FROM_HOST_{self.used_cloud_vars[self.current_var]}",
                        f"{response_part}.{request_id}{iteration_string}1")
                except Exception:
                    Thread(target=self.call_event, args=["on_disconnect"]).start()
                self.current_var += 1
                if self.current_var == len(self.used_cloud_vars):
                    self.current_var = 0

            else:
                try:
                    self.cloud.set_var(
                        f"FROM_HOST_{self.used_cloud_vars[self.current_var]}",
                        f"{remaining_response}.{request_id}{validation}")
                except Exception:
                    Thread(target=self.call_event, args=["on_disconnect"]).start()
                self.current_var += 1
                if self.current_var == len(self.used_cloud_vars):
                    self.current_var = 0
                remaining_response = ""
                
            time.sleep(self.cloud.ws_shortterm_ratelimit)

        self.idle_since = time.time()

    # -- Register and handle incoming requests --

    def on_set(self, activity):
        """
        This function is automatically called on cloud activites by the underlying cloud events that this CloudRequests class inherits from
        It registers incoming cloud activity and (if request.thread is True) runs them directly or (else) adds detected request to the .received_requests list
        """
        # Note for contributors: All functions called in this on_set function MUST be executed in threads because this function blocks the cloud events receiver, which is usually not a problem (because of the websocket buffer) but can cause problems in rare cases
        if activity.var == "TO_HOST" and "." in activity.value:
            # Parsing the received request
            raw_request, request_id = activity.value.split(".")

            if request_id in self.responded_request_ids:
                # => The received request has already been answered, meaning this activity has already been received
                return

            if activity.value[0] == "-":
                # => The received request is actually part of a bigger request
                if not request_id in self.request_parts:
                    self.request_parts[request_id] = []
                self.request_parts[request_id].append(raw_request[1:])
                return
            
            self.responded_request_ids.insert(0, request_id)
            self.responded_request_ids = self.responded_request_ids[:35]

            # If the request consists of multiple parts: Put together the parts to get the whole raw request string
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
            request_name = arguments.pop(0)#
            
            # Check if the request is unknown:
            if request_name not in self._requests:
                print(
                    f"Warning: Client received an unknown request called '{request_name}'"
                )
                Thread(target=self.call_event, args=["on_unknown_request", [
                    ReceivedRequest(request_name=request,
                        requester=activity.user,
                        timestamp=activity.timestamp,
                        arguments=arguments,
                        request_id=request_id)
                ]]).start()
                return
            
            received_request = ReceivedRequest(
                request = self._requests[request_name],
                requester=activity.user,
                timestamp=activity.timestamp,
                arguments=arguments,
                request_id=request_id
            )
            if received_request.request.thread:
                self.executed_requests[request_id] = received_request
                Thread(target=received_request.request, args=[received_request]).start() # Execute the request function directly in a thread
            else:
                self.received_requests.append(received_request)
                with self.executer_condition:
                    self.executer_condition.notify() # Activate the ._executer process so that it handles the received request
    
    def _executer(self):
        """
        A process that detects new requests in .received_requests, moves them to .executed_requests and executes them. Only requests not running in threads are handled in this process.
        """
        # If .no_packet_loss is enabled and the cloud provides logs, the logs are used to check whether there are cloud activities that were not received over the cloud connection used by the underlying cloud events
        use_extra_data = (self.no_packet_loss and hasattr(self.cloud, "logs"))
        
        with self.executer_condition:
            self.executer_condition.wait() # Wait for requests to be received
            while self.executer_thread is not None: # If self.executer_thread is None, it means cloud requests were stopped using .stop()
                
                if self.received_requests == [] and use_extra_data:
                    Thread(target=self.on_reconnect).start()

                while self.received_requests != []:
                    received_request = self.received_requests.pop(0)
                    self.executed_requests[received_request.request_id] = received_request
                    received_request.request(received_request) # Execute the request function

                    if use_extra_data:
                        Thread(target=self.on_reconnect).start()
                
                self.executer_condition.wait(timeout = 2.5 if use_extra_data else None) # Wait for requests to be received

    def _responder(self):
        """
        A process that detects incoming request outputs in .request_outputs and handles them by sending them back to the Scratch project, also removes the corresponding ReceivedRequest object from .executed_requests
        """
        with self.responder_condition:
            while self.responder_thread is not None: # If self.responder_thread is None, it means cloud requests were stopped using .stop()
                self.responder_condition.wait() # Wait for executed requests to respond
                print("got responder notification")
                
                while self.request_outputs != []:
                    if self.respond_order == "finish":
                        output_obj = self.request_outputs.pop(0)
                    else:
                        output_obj = min(self.request_outputs, key=lambda x : x[self.respond_order])
                        self.request_outputs.remove(output_obj)
                    received_request = self.executed_requests.pop(output_obj["request_id"])
                    self._parse_output(received_request, output_obj["output"])
                
    def on_reconnect(self):
        """
        Called when the underlying cloud events reconnect. Makes sure that no requests are missed in this case.
        """
        extradata = self.cloud.logs(limit=35)[::-1] # Reverse result so oldest activity is first
        for activity in extradata:
            if activity.timestamp < self.startup_time:
                continue
            self.on_set(activity) # Read in the fetched activity
        
    # -- Other stuff --

    def stop(self):
        """
        Stops the request handler and all associated threads forever.
        """
        # Override the .stop function from BaseEventHandler to make sure the ._executer and ._responder threads are also terminated
        super().stop()
        self.executer_thread = None
        self.responder_thread = None
        with self.executer_condition:
            with self.responder_condition:
                self.executer_condition.notify()
                self.responder_condition.notify()

    def credit_check(self):
        try:
            p = project.Project(id=self.cloud.project_id)
            if not p.update(): # can't get project, probably because it's unshared (no authentication is used for getting it)
                print("If you use CloudRequests, please credit TimMcCool!")
                return
            description = (str(p.instructions) + str(p.notes)).lower()
            if not ("timmccool" in description or "timmcool" in description or "timccool" in description or "timcool" in description):
                print("It was detected that no credit was given in the project description! Please credit TimMcCool when using CloudRequests.")
            else:
                print("Thanks for giving credit for CloudRequests!")
        except Exception:
            print("If you use CloudRequests, please credit TimMcCool!")

    def run(self):
        # Was changed to .start(), but .run() is kept for backwards compatibility
        print("Warning: requests.run() was changed to requests.start() in v2.0. .run() will be removed in a future version")
        self.start()
