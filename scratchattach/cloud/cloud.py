from ._base import BaseCloud

class ScratchCloud(BaseCloud):

    def __init__(self, *, project_id, _session=None):
        super().__init__()
        
        # Required attributes
        self.project_id = project_id
        self._session = _session
        self.cloud_host = "wss://clouddata.scratch.mit.edu"
        
        # Optional attributes
        self.length_limit = 256
        self.cookie = "scratchsessionsid=" + self._session.id + ";"
        self.origin = "https://scratch.mit.edu"

    def connect(self):
        self.assert_auth() # Connecting to Scratch's cloud websocket requires a login to the Scratch website
        super().connect()

    def set_var(self, variable, value):
        self.assert_auth() # Setting a cloud var requires a login to the Scratch website
        super().set_var(variable, value)

class TwCloud(BaseCloud):

    def __init__(self, *, project_id, _session=None, cloud_host="wss://clouddata.turbowarp.org", purpose="", contact=""):
        super().__init__()
        
        # Required attributes
        self.project_id = project_id
        self._session = _session
        self.cloud_host = cloud_host
        
        # Optional attributes
        self.ws_ratelimit = 0 # TurboWarp doesn't enforce a wait time between cloud variable sets
        self.length_limit = 100000 # TurboWarp doesn't enforce a cloud variable length
        purpose_string = ""
        if purpose != "" or contact != "":
            purpose_string = f" (Purpose:{purpose}; Contact:{contact})"
        self.header = {"User-Agent":f"scratchattach/2.0.0{purpose_string}"}

    def connect(self):
        self.assert_auth() # Connecting to Scratch's cloud websocket requires a login to the Scratch website
        super().connect()

    def set_var(self, variable, value):
        self.assert_auth() # Setting a cloud var requires a login to the Scratch website
        super().set_var(variable, value)
