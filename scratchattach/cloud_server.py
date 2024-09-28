from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from threading import Thread
from .utils import exceptions
import json
import time

class TwCloudServer(WebSocket):

    def handleMessage(self):
        return

    def handleConnected(self):
        return

    def handleClose(self):
        return

def start_tw_cloud_server(hostname='127.0.0.1', port=8080, *, thread=False, length_limit=None, allow_non_numeric=True, whitelisted_projects=None):
    """
    Starts a websocket server which can be used with TurboWarp's ?cloud_host URL parameter.
    
    Prints out the websocket address in the console.
    """
    print(f"Serving websocket server: ws://{hostname}:{port}")
    try:

        server = SimpleWebSocketServer(hostname, port=port, websocketclass=TwCloudServer)

        server.value_length_limit=length_limit
        server.value_allow_numeric=allow_non_numeric
        server.whitelisted_projects=whitelisted_projects
        server.tw_projects = {}
        server.tw_userdata = {}
        server.tw_users = []

        if thread:
            Thread(target=server.serveforever).start()
            return server
        else:
            server.serveforever()
    except Exception as e:
        raise exceptions.WebsocketServerError(str(e))
    

