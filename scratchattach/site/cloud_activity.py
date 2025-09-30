from __future__ import annotations

import time
from typing import Union, TypeGuard, Optional
from dataclasses import dataclass, field
import warnings

from scratchattach.cloud import _base
from scratchattach.utils import exceptions
from scratchattach.site import project, user
from ._base import BaseSiteComponent
from . import typed_dicts, session

@dataclass
class CloudActivity(BaseSiteComponent[Union[typed_dicts.CloudActivityDict, typed_dicts.CloudLogActivityDict]]):
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
    username: str = field(kw_only=True, default="")
    var: str = field(kw_only=True, default="")
    name: str = field(kw_only=True, default="")
    type: str = field(kw_only=True, default="set")
    timestamp: float = field(kw_only=True, default=0.0)
    value: Union[float, int, str] = field(kw_only=True, default="0.0")
    cloud: _base.AnyCloud = field(kw_only=True, default_factory=lambda : _base.DummyCloud())
    _session: Optional[session.Session] = field(kw_only=True, default=None)

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
        warnings.warn("CloudActivity objects can't be updated", exceptions.InvalidUpdateWarning)
        return False # Objects of this type cannot be updated

    def __eq__(self, activity2):
        # CloudLogEvents needs to check if two activites are equal (to finde new ones), therefore CloudActivity objects need to be comparable
        return self.user == activity2.user and self.type == activity2.type and self.timestamp == activity2.timestamp and self.value == activity2.value and self.name == activity2.name
    
    def _update_from_dict(self, data: Union[typed_dicts.CloudActivityDict, typed_dicts.CloudLogActivityDict]) -> bool:
        def is_cloud_log_activity(activity: Union[typed_dicts.CloudActivityDict, typed_dicts.CloudLogActivityDict]) -> TypeGuard[typed_dicts.CloudLogActivityDict]:
            return "verb" in activity
        def is_cloud_activity(activity: Union[typed_dicts.CloudActivityDict, typed_dicts.CloudLogActivityDict]) -> TypeGuard[typed_dicts.CloudActivityDict]:
            return "method" in activity
        self.name = data["name"]
        self.var = data["name"]
        self.value = data["value"]
        if is_cloud_log_activity(data):
            self.user = data["user"]
            self.username = data["user"]
            self.timestamp = data["timestamp"]
            self.type = data["verb"].removesuffix("_var")
        elif is_cloud_activity(data):
            self.type = data["method"]
        if "cloud" in data:
            self.cloud = data["cloud"]
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
        return self._make_linked_object("username", self.username, user.User, exceptions.UserNotFound)

    def project(self) -> Optional[project.Project]:
        """
        Returns the project where the cloud activity was performed as scratchattach.project.Project object
        """
        def make_linked(cloud: _base.BaseCloud) -> project.Project:
            return self._make_linked_object("id", cloud.project_id, project.Project, exceptions.ProjectNotFound)
        if self.cloud is None:
            return None
        cloud = self.cloud
        if not isinstance(cloud, _base.BaseCloud):
            return None
        return make_linked(cloud)

