#----- The cloud request handler class
from . import _cloud
import time
from ._encoder import *
import math

class CloudRequests:

    def __init__(self, cloud_connection : _cloud.CloudConnection, *, ignore_exceptions=True):
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

    def _respond(self, request_id, response):

        if self.idle_since + 8 < time.time():
            self.connection._connect(cloud_host=None)
            self.connection._handshake()

        remaining_response = str(response)


        i = 0
        while not remaining_response == "":
            if len(remaining_response) > 220:
                response_part = remaining_response[:220]
                remaining_response = remaining_response[220:]

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
                            self._respond(request_id, Encoding.encode(f"Error: Unknown request"))
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
                                self._respond(request_id, Encoding.encode("Error: Client received too many arguments, not enough arguments or invalid arguments"))
                                print(f"Error in request '{request}': Client received too many arguments, not enough arguments or invalid arguments.\nOriginal error: {e}")
                            except Exception as e:
                                self._respond(request_id, Encoding.encode(f"Error: Check the Python console"))
                                if self.ignore_exceptions:
                                    print(f"Caught error in request '{request}': {e}")
                                else:
                                    print(f"Exception in request '{request}':")
                                    raise(e)

                        if len(str(output)) > 3000:
                            length_output = len(str(output))
                            print(f"Error in request '{request}': Output too large!\nMax. output content length: 3000 characters.\nOutput length of {request}: {length_output} characters")
                            output = Encoding.encode("Error: Output too large, check Python console for details.")

                        else:
                            if not isinstance(output, list):
                                output = Encoding.encode(output)
                            else:
                                input = output
                                output = ""
                                for i in input:
                                    output += Encoding.encode(i)
                                    output += "89"
                        self._respond(request_id, output)
                        self.last_timestamp = activity['timestamp']
                self.last_data = data
