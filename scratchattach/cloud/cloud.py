"""v2 ready: ScratchCloud, TwCloud and CustomCloud classes"""

from __future__ import annotations

from ._base import BaseCloud
from typing import Type
from ..utils.requests import Requests as requests
from ..utils import exceptions, commons
from ..site import cloud_activity


class ScratchCloud(BaseCloud):
    def __init__(self, *, project_id, _session=None):
        super().__init__()
        
        self.project_id = project_id

        # Configure this object's attributes specifically for being used with Scratch's cloud:
        self.cloud_host = "wss://clouddata.scratch.mit.edu"
        self.length_limit = 256
        self._session = _session
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
    
    def set_vars(self, var_value_dict, *, intelligent_waits=True):
        self._assert_auth() 
        super().set_vars(var_value_dict, intelligent_waits=intelligent_waits)

    def logs(self, *, filter_by_var_named=None, limit=100, offset=0) -> list[cloud_activity.CloudActivity]:
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
            if filter_by_var_named is not None:
                filter_by_var_named = filter_by_var_named.removeprefix("☁ ")
                data = list(filter(lambda k: k["name"] == "☁ "+filter_by_var_named, data))
            for x in data:
                x["cloud"] = self
            return commons.parse_object_list(data, cloud_activity.CloudActivity, self._session, "name")
        except Exception as e:
            raise exceptions.FetchError(str(e))

    def get_var(self, var, *, use_logs=False):
        var = var.removeprefix("☁ ")
        if self._session is None or use_logs:
            filtered = self.logs(limit=100, filter_by_var_named="☁ "+var)
            if len(filtered) == 0:
                return None
            return filtered[0].value
        else:
            if self.recorder is None:
                initial_values = self.get_all_vars(use_logs=True)
                return super().get_var("☁ "+var, recorder_initial_values=initial_values)
            else:
                return super().get_var("☁ "+var)

    def get_all_vars(self, *, use_logs=False):
        if self._session is None or use_logs:
            logs = self.logs(limit=100)
            logs.reverse()
            clouddata = {}
            for activity in logs:
                clouddata[activity.name] = activity.value
            return clouddata
        else:
            if self.recorder is None:
                initial_values = self.get_all_vars(use_logs=True)
                return super().get_all_vars(recorder_initial_values=initial_values)
            else:
                return super().get_all_vars()

    def events(self, *, use_logs=False):
        if self._session is None or use_logs:
            from ..eventhandlers.cloud_events import CloudLogEvents
            return CloudLogEvents(self)
        else:
            return super().events()


class TwCloud(BaseCloud):
    def __init__(self, *, project_id, cloud_host="wss://clouddata.turbowarp.org", purpose="", contact="",
                 _session=None):
        super().__init__()
        
        self.project_id = project_id
        
        # Configure this object's attributes specifically for being used with TurboWarp's cloud:
        self.cloud_host = cloud_host
        self.ws_shortterm_ratelimit = 0 # TurboWarp doesn't enforce a wait time between cloud variable sets
        self.ws_longterm_ratelimit = 0
        self.length_limit = 100000 # TurboWarp doesn't enforce a cloud variable length
        purpose_string = ""
        if purpose != "" or contact != "":
            purpose_string = f" (Purpose:{purpose}; Contact:{contact})"
        self.header = {"User-Agent":f"scratchattach/2.0.0{purpose_string}"}

class CustomCloud(BaseCloud):

    def __init__(self, *, project_id, cloud_host, **kwargs):
        super().__init__()
        
        self.project_id = project_id
        self.cloud_host = cloud_host

        # Configure this object's attributes specifically for the cloud that the developer wants to connect to:
        # -> For this purpose, all additional keyword arguments (kwargs) will be set as attributes of the CustomCloud object
        # This allows the maximum amount of attribute customization
        # See the docstring for the cloud._base.BaseCloud class to find out what attributes can be set / specified as keyword args
        self.__dict__.update(kwargs)

        # If even more customization is needed, the developer can create a class inheriting from cloud._base.BaseCloud to override functions like .set_var etc.


def get_cloud(project_id, *, CloudClass:Type[BaseCloud]=ScratchCloud) -> BaseCloud:
    """
    Connects to a cloud (by default Scratch's cloud) as logged out user.

    Warning:
        Since this method doesn't connect a login / session to the returned object, setting Scratch cloud variables won't be possible with it.

        To set Scratch cloud variables, use `scratchattach.site.session.Session.connect_scratch_cloud` instead.

    Args:
        project_id:
    
    Keyword arguments:
        CloudClass: The class that the returned object should be of. By default this class is scratchattach.cloud.ScratchCloud.

    Returns:
        Type[scratchattach.cloud._base.BaseCloud]: An object representing the cloud of a project. Can be of any class inheriting from BaseCloud.
    """
    print("Warning: To set Scratch cloud variables, use session.connect_cloud instead of get_cloud")
    return CloudClass(project_id=project_id)

def get_scratch_cloud(project_id):
    """
    Warning:
        Since this method doesn't connect a login / session to the returned object, setting Scratch cloud variables won't be possible with it.

        To set Scratch cloud variables, use `scratchattach.Session.connect_scratch_cloud` instead.

        
    Returns:
        scratchattach.cloud.ScratchCloud: An object representing the Scratch cloud of a project.
    """
    print("Warning: To set Scratch cloud variables, use session.connect_scratch_cloud instead of get_scratch_cloud")
    return ScratchCloud(project_id=project_id)

def get_tw_cloud(project_id, *, purpose="", contact="", cloud_host="wss://clouddata.turbowarp.org"):
    """
    Returns:
        scratchattach.cloud.TwCloud: An object representing the TurboWarp cloud of a project.
    """
    return TwCloud(project_id=project_id, purpose=purpose, contact=contact, cloud_host=cloud_host)
