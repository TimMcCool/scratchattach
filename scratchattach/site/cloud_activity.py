import time
from ._base import BaseSiteComponent

class CloudActivity(BaseSiteComponent):
    """
    Represents a cloud activity (a cloud variable set / creation / deletion).

    Attributes:

    .user: The user who caused the cloud event (the user who added / set / deleted the cloud variable)

    .var: The name of the cloud variable that was updated (specified without the cloud emoji)

    .name: The name of the cloud variable that was updated (specified without the cloud emoji)

    .timestamp: Then timestamp of when the action was performed

    .value: If the cloud variable was set, then this attribute provides the value the cloud variable was set to
    
    .cloud: The cloud (as object inheriting from scratchattach.Cloud.BaseCloud) that the cloud activity corresponds to
    """

    def __init__(self, **entries):
        # Set attributes every Activity object needs to have:
        self.raw = None
        self._session = None
        self.cloud = None
        self.user = None
        self.type = None
        self.timestamp = time.time()

        # Update attributes from entries dict:
        self.__dict__.update(entries)

    def update(self):
        return False # Objects of this type cannot be update
    
    def _update_from_dict(self, data) -> bool:
        try: self.name = data["name"]
        except Exception: pass
        try: self.var = data["name"]
        except Exception: pass
        try: self.value = data["value"]
        except Exception: pass
        try: self.user = data["user"]
        except Exception: pass
        try: self.timestamp = data["timestamp"]
        except Exception: pass
        try: self.type = data["verb"]
        except Exception: pass
        try: self.type = data["method"]
        except Exception: pass
        try: self.cloud = data["cloud"]
        except Exception: pass

    def load_log_data(self):
        if self.cloud is None:
            print("Warning: There aren't cloud logs available for this cloud, therefore the user and exact timestamp can't be loaded")
        else:
            if hasattr(self.cloud, "logs"):
                logs = self.cloud.logs(filter_by_var_named=self.var)
                matching = list(filter(lambda x: x.value == self.value and x.timestamp <= self.timestamp, logs))
                if matching == []:
                    return False
                activity = matching[0]
                self.user = activity.user
                self.timestamp = activity.timestamp
                return True
            else:
                print("Warning: There aren't cloud logs available for this cloud, therefore the user and exact timestamp can't be loaded")
        return False
    