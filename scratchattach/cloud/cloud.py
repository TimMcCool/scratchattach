from ._base import BaseCloud
from typing import Type
from ..utils.requests import Requests as requests
from ..utils import exceptions

class ScratchCloud(BaseCloud):

    def __init__(self, *, project_id, _session=None):
        super().__init__()
        
        # Required attributes
        self.project_id = project_id
        self._session = _session
        self.cloud_host = "wss://clouddata.scratch.mit.edu"
        
        # Optional attributes
        self.length_limit = 256
        if self._session is not None:
            self.username = self._session.username
            self.cookie = "scratchsessionsid=" + self._session.id + ";"
            self.origin = "https://scratch.mit.edu"

    def connect(self):
        self._assert_auth() # Connecting to Scratch's cloud websocket requires a login to the Scratch website
        super().connect()

    def set_var(self, variable, value):
        self._assert_auth() # Setting a cloud var requires a login to the Scratch website
        super().set_var(variable, value)
    
    def logs(self, *, filter_by_var_named=None, limit=100, offset=0):
        """
        Gets the data from Scratch's clouddata logs.
        
        Keyword Arguments:
            filter_by_var_named (str or None): If you only want to get data for one cloud variable, set this argument to its name.
            limit (int): Max. amount of returned activity.
            offset (int): Offset of the first activity in the returned list.
            log_url (str): If you want to get the clouddata from a cloud log API different to Scratch's normal cloud log API, set this argument to the URL of the API. Only set this argument if you know what you are doing. If you want to get the clouddata from the normal API, don't put this argument.
        """
        try:
            data = requests.get(f"https://clouddata.scratch.mit.edu/logs?projectid={self.project_id}&limit={limit}&offset={offset}", timeout=10).json()
            if filter_by_var_named is None:
                return data
            else:
                return list(filter(lambda k: k["name"] == "☁ "+filter_by_var_named, data))
        except Exception as e:
            return exceptions.FetchError(str(e))

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

def get_cloud(project_id, *, CloudClass:Type[BaseCloud]=ScratchCloud) -> Type[BaseCloud]:
    """
    Connects to a cloud (by default Scratch's cloud) as logged out user.

    Warning:
        Since this method doesn't connect a login / session to the returned object, setting Scratch cloud variables won't be possible with it.

        To set Scratch cloud variables, use `scratchattach.Session.connect_scratch_cloud` instead.

    Args:
        project_id:
    
    Keyword arguments:
        CloudClass: The class that the returned object should be of. By default this class is scratchattach.cloud.ScratchCloud.

    Returns:
        Type[scratchattach.cloud.BaseCloud]: An object representing the cloud of a project. Can be of any class inheriting from BaseCloud.
    """
    print("Warning: To set Scratch cloud variables, use session.connect_cloud instead of get_cloud")
    return CloudClass(project_id=project_id)

def get_scratch_cloud(project_id, *, purpose="", contact=""):
    """
    Warning:
        Since this method doesn't connect a login / session to the returned object, setting Scratch cloud variables won't be possible with it.

        To set Scratch cloud variables, use `scratchattach.Session.connect_scratch_cloud` instead.

        
    Returns:
        scratchattach.cloud.ScratchCloud: An object representing the Scratch cloud of a project.
    """
    print("Warning: To set Scratch cloud variables, use session.connect_scratch_cloud instead of get_scratch_cloud")
    return ScratchCloud(project_id=project_id, purpose=purpose, contact=contact)

def get_tw_cloud(project_id, *, purpose="", contact=""):
    """
    Returns:
        scratchattach.cloud.TwCloud: An object representing the TurboWarp cloud of a project.
    """
    return TwCloud(project_id=project_id, purpose=purpose, contact=contact)
