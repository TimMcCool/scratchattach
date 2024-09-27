from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from threading import Thread
from .utils import exceptions

class TwCloudServer(WebSocket):

    def __init__(self, *, length_limit=None, allow_non_numeric=True, whitelisted_projects=None):
        # Config server
        self.length_limit=length_limit
        self.allow_non_numeric=allow_non_numeric
        self.whitelisted_projects=whitelisted_projects

    def handleMessage(self):
        # echo message back to client
        self.sendMessage(self.data)

    def handleConnected(self):
        print(self.address, 'connected')

    def handleClose(self):
        print(self.address, 'closed')
    
def start_tw_cloud_server(hostname='0.0.0.0', port=8080, *, thread=False):
    print(f"Serving websocket server: wss://{hostname}:{port}")
    try:
        server = SimpleWebSocketServer(hostname, port, TwCloudServer)
        if thread:
            Thread(target=server.serveforever).start()
            return server
        else:
            server.serveforever()
    except Exception as e:
        raise exceptions.WebsocketServerError(str(e))
