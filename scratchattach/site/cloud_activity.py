from __future__ import annotations

import time
from ._base import BaseSiteComponent



class CloudActivity(BaseSiteComponent):
    """
    Represents a cloud activity (a cloud variable set / creation / deletion).

    Attributes:

    :.username: The user who caused the cloud event (the user who added / set / deleted the cloud variable)

    :.var: The name of the cloud variable that was updated (specified without the cloud emoji)

    :.name: The name of the cloud variable that was updated (specified without the cloud emoji)

    :.type: The activity type

    :.timestamp: Then timestamp of when the action was performed

    :.value: If the cloud variable was set, then this attribute provides the value the cloud variable was set to
    
    :.cloud: The cloud (as object inheriting from scratchattach.Cloud.BaseCloud) that the cloud activity corresponds to
    """

    def __init__(self, **entries):
        # Set attributes every CloudActivity object needs to have:
        self._session = None
        self.cloud = None
        self.user = None
        self.username = None
        self.type = None
        self.timestamp = time.time()

        # Update attributes from entries dict:
        self.__dict__.update(entries)

    def update(self):
        print("Warning: CloudActivity objects can't be updated")
        return False # Objects of this type cannot be updated

    def __eq__(self, activity2):
        # CloudLogEvents needs to check if two activites are equal (to finde new ones), therefore CloudActivity objects need to be comparable
        return self.user == activity2.user and self.type == activity2.type and self.timestamp == activity2.timestamp and self.value == activity2.value and self.name == activity2.name
    
    def _update_from_dict(self, data) -> bool:
        try: self.name = data["name"]
        except Exception: pass
        try: self.var = data["name"]
        except Exception: pass
        try: self.value = data["value"]
        except Exception: pass
        try: self.user = data["user"]
        except Exception: pass
        try: self.username = data["user"]
        except Exception: pass
        try: self.timestamp = data["timestamp"]
        except Exception: pass
        try: self.type = data["verb"].replace("_var","")
        except Exception: pass
        try: self.type = data["method"]
        except Exception: pass
        try: self.cloud = data["cloud"]
        except Exception: pass
        return True

    def load_log_data(self):
        if self.cloud is None:
            print("Warning: There aren't cloud logs available for this cloud, therefore the user and exact timestamp can't be loaded")
        else:
            if hasattr(self.cloud, "logs"):
                logs = self.cloud.logs(filter_by_var_named=self.var, limit=100)
                matching = list(filter(lambda x: x.value == self.value and x.timestamp <= self.timestamp, logs))
                if matching == []:
                    return False
                activity = matching[0]
                self.username = activity.username
                self.user = activity.username
                self.timestamp = activity.timestamp
                return True
            else:
                print("Warning: There aren't cloud logs available for this cloud, therefore the user and exact timestamp can't be loaded")
        return False
    
    def actor(self):
        """
        Returns the user that performed the cloud activity as scratchattach.user.User object
        """
        if self.username is None:
            return None
        from ..site import user
        from ..utils import exceptions
        return self._make_linked_object("username", self.username, user.User, exceptions.UserNotFound)

    def project(self):
        """
        Returns the project where the cloud activity was performed as scratchattach.project.Project object
        """
        if self.cloud is None:
            return None
        from ..site import project
        from ..utils import exceptions
        return self._make_linked_object("id", self.cloud.project_id, project.Project, exceptions.ProjectNotFound)

