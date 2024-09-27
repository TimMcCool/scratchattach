"""v2 ready: Activity and CloudActivity class"""

import json
import re
import time

from . import user
from . import session
from . import project
from . import studio
from . import forum, comment
from ..utils import exceptions
from ._base import BaseSiteComponent
from ..utils.commons import headers
from bs4 import BeautifulSoup

from ..utils.requests import Requests as requests

class Activity(BaseSiteComponent):

    '''
    Represents a Scratch activity (message or other user page activity)
    '''

    def str(self):
        return str(self.raw)

    def __init__(self, **entries):

        # Set attributes every Activity object needs to have:
        self.raw = None
        self._session = None

        # Update attributes from entries dict:
        self.__dict__.update(entries)

    def update():
        return False # Objects of this type cannot be updated

    def _update_from_dict(self, data):
        self.__dict__.update(data)
        return True

    def _update_from_html(self, data):

        time=data.find('div').find('span').findNext().findNext().text.strip()

        if '\xa0' in time:
            while '\xa0' in time: time=time.replace('\xa0', ' ')

        self.time = time
        self.actor_username=(data.find('div').find('span').text)

        self.target_name=(data.find('div').find('span').findNext().text)
        self.target_link=(data.find('div').find('span').findNext()["href"])
        self.target_id=(data.find('div').find('span').findNext()["href"].split("/")[-2])

        self.type=data.find('div').find_all('span')[0].next_sibling.strip()
        if self.type == "loved":
            self.type = "loveproject"
        if self.type == "favorited":
            self.type = "favoriteproject"
        if "curator" in self.type:
            self.type = "becomecurator"
        if "shared" in self.type:
            self.type = "shareproject"
        if "is now following" in self.type:
            if "users" in self.target_link:
                self.type = "followuser"
            else:
                self.type = "followstudio"

        return True

    def actor(self):
        """
        Returns the user that performed the activity as User object
        """
        return self._make_linked_object("username", self.actor_username, user.User, exceptions.UserNotFound)

    def target(self):
        """
        Returns the activity's target (depending on the activity, this is either a User, Project, Studio or Comment object).
        May also return None if the activity type is unknown.
        """
        
        if "project" in self.type: # target is a project
            if "target_id" in self.__dict__:
                return self._make_linked_object("id", self.target_id, project.Project, exceptions.ProjectNotFound)
            if "project_id" in self.__dict__:
                return self._make_linked_object("id", self.project_id, project.Project, exceptions.ProjectNotFound)
            
        if self.type == "becomecurator" or self.type == "followstudio": # target is a studio
            if "target_id" in self.__dict__:
                return self._make_linked_object("id", self.target_id, studio.Studio, exceptions.StudioNotFound)
            if "gallery_id" in self.__dict__:
                return self._make_linked_object("id", self.gallery_id, studio.Studio, exceptions.StudioNotFound)
            # NOTE: the "becomecurator" type is ambigous - if it is inside the studio activity tab, the target is the user who joined
            if "username" in self.__dict__:
                return self._make_linked_object("username", self.username, user.User, exceptions.UserNotFound)
            
        if self.type == "followuser" or "curator" in self.type: # target is a user
            if "target_id" in self.__dict__:
                return self._make_linked_object("username", self.target_id, user.User, exceptions.UserNotFound)
            if "followed_username" in self.__dict__:
                return self._make_linked_object("username", self.followed_username, user.User, exceptions.UserNotFound)
        if "recipient_username" in self.__dict__: # the recipient_username field always indicates the target is a user
            return self._make_linked_object("username", self.recipient_username, user.User, exceptions.UserNotFound)
        
        if self.type == "addcomment": # target is a comment
            if self.comment_type == 0:
                _c = project.Project(id=self.comment_obj_id, author_name=self._session.username, _session=self._session).comment_by_id(self.comment_id)
            if self.comment_type == 1:
                _c = user.User(username=self.comment_obj_title, _session=self._session).comment_by_id(self.comment_id)
            if self.comment_type == 2:
                _c = user.User(id=self.comment_obj_id, _session=self._session).comment_by_id(self.comment_id)          
            return _c
        
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
        try: self.username = data["user"]
        except Exception: pass
        try: self.timestamp = data["timestamp"]
        except Exception: pass
        try: self.type = data["verb"]
        except Exception: pass
        try: self.type = data["method"]
        except Exception: pass

    def load_username_and_timestamp(self):
        if self.cloud is None:
            print("Warning: There aren't cloud logs available for this cloud, therefore the user and exact timestamp can't be loaded")
        else:
            if hasattr(self.cloud, "logs"):
                logs = self.cloud.logs(filter_by_var_named=self.var)
                activity = list(filter(lambda x: x.value == self.value and x.timestamp < self.timestamp, logs))
                self.username = activity.username
                self.timestamp = activity.timestamp
                return True
            else:
                print("Warning: There aren't cloud logs available for this cloud, therefore the user and exact timestamp can't be loaded")
        return False
    