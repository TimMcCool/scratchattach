"""Activity and CloudActivity class"""
from __future__ import annotations

import html
import warnings

from dataclasses import dataclass
from typing import Optional, Any
from enum import Enum
from datetime import datetime

from bs4 import Tag

from . import user, project, studio, session, forum
from .typed_dicts import ActivityDict
from ._base import BaseSiteComponent
from scratchattach.utils import exceptions

class ActivityTypes(Enum):
    loveproject = "loveproject"
    favoriteproject = "favoriteproject"
    becomecurator = "becomecurator"
    followuser = "followuser"
    followstudio = "followstudio"
    shareproject = "shareproject"
    remixproject = "remixproject"
    becomeownerstudio = "becomeownerstudio"
    addcomment = "addcomment"
    curatorinvite = "curatorinvite"
    userjoin = "userjoin"
    studioactivity = "studioactivity"
    forumpost = "forumpost"
    updatestudio = "updatestudio"
    createstudio = "createstudio"
    promotetomanager = "promotetomanager"
    updateprofile = "updateprofile"
    removeprojectfromstudio = "removeprojectfromstudio"
    addprojecttostudio = "addprojecttostudio"
    performaction = "performaction"

@dataclass
class Activity(BaseSiteComponent):
    """
    Represents a Scratch activity (message or other user page activity)
    """
    _session: Optional[session.Session] = None
    raw: Any = None

    id: Optional[int] = None
    actor_username: Optional[str] = None

    project_id: Optional[int] = None
    gallery_id: Optional[int] = None
    username: Optional[str] = None
    followed_username: Optional[str] = None
    recipient_username: Optional[str] = None
    title: Optional[str] = None
    project_title: Optional[str] = None
    gallery_title: Optional[str] = None
    topic_title: Optional[str] = None
    topic_id: Optional[int] = None
    target_name: Optional[str] = None
    target_id: Optional[int | str] = None

    parent_title: Optional[str] = None
    parent_id: Optional[int] = None

    comment_type: Optional[int] = None
    comment_obj_id = None
    comment_obj_title: Optional[str] = None
    comment_id: Optional[int] = None
    comment_fragment: Optional[str] = None

    changed_fields: Optional[dict[str, str]] = None
    is_reshare: Optional[bool] = None

    datetime_created: Optional[datetime] = None
    datetime_created_raw: Optional[str] = None
    time: Any = None
    type: Optional[ActivityTypes] = None

    def __repr__(self):
        return f"Activity({repr(self.raw)})"

    def __str__(self):
        return '-A ' + ' '.join(self.parts)

    @property
    def parts(self):
        """
        Return format: [actor username] + N * [action, object]
        :return: A list of parts of the message. Join the parts to get a readable version, which is done with str(activity)
        """
        match self.type:
            case ActivityTypes.loveproject:
                return [f"{self.actor_username}", "loved", f"-P {self.title!r} ({self.project_id})"]
            case ActivityTypes.favoriteproject:
                return [f"{self.actor_username}", "favorited", f"-P {self.project_title!r} ({self.project_id})"]
            case ActivityTypes.becomecurator:
                return [f"{self.actor_username}", "now curating", f"-S {self.title!r} ({self.gallery_id})"]
            case ActivityTypes.followuser:
                return [f"{self.actor_username}", "followed", f"-U {self.followed_username}"]
            case ActivityTypes.followstudio:
                return [f"{self.actor_username}", "followed", f"-S {self.title!r} ({self.gallery_id})"]
            case ActivityTypes.shareproject:
                return [f"{self.actor_username}", "reshared" if self.is_reshare else "shared",
                        f"-P {self.title!r} ({self.project_id})"]
            case ActivityTypes.remixproject:
                return [f"{self.actor_username}", "remixed",
                        f"-P {self.parent_title!r} ({self.parent_id}) as -P {self.title!r} ({self.project_id})"]
            case ActivityTypes.becomeownerstudio:
                return [f"{self.actor_username}", "became owner of", f"-S {self.gallery_title!r} ({self.gallery_id})"]

            case ActivityTypes.addcomment:
                ret = [self.actor_username, "commented on"]

                match self.comment_type:
                    case 0:
                        # project
                        ret.append(f"-P {self.comment_obj_title!r} ({self.comment_obj_id}")
                    case 1:
                        # user
                        ret.append(f"-U {self.comment_obj_title}")

                    case 2:
                        # studio
                        ret.append(f"-S {self.comment_obj_title!r} ({self.comment_obj_id}")

                    case _:
                        raise ValueError(f"Unknown comment type: {self.comment_type}")

                ret[-1] += f"#{self.comment_id})"

                ret.append(f"{html.unescape(self.comment_fragment)}")

                return ret

            case ActivityTypes.curatorinvite:
                return [f"{self.actor_username}", "invited you to curate", f"-S {self.title!r} ({self.gallery_id})"]

            case ActivityTypes.userjoin:
                # This is also the first message you get - 'Welcome to Scratch'
                return [f"{self.actor_username}", "joined Scratch"]

            case ActivityTypes.studioactivity:
                # the actor username should be systemuser
                return [f"{self.actor_username}", 'Studio activity', '', f"-S {self.title!r} ({self.gallery_id})"]

            case ActivityTypes.forumpost:
                return [f"{self.actor_username}", "posted in", f"-F {self.topic_title} ({self.topic_id})"]

            case ActivityTypes.updatestudio:
                return [f"{self.actor_username}", "updated", f"-S {self.gallery_title} ({self.gallery_id})"]

            case ActivityTypes.createstudio:
                return [f"{self.actor_username}", "created", f"-S {self.gallery_title} ({self.gallery_id})"]

            case ActivityTypes.promotetomanager:
                return [f"{self.actor_username}", "promoted", f"-U {self.recipient_username}", "in",
                        f"-S {self.gallery_title} ({self.gallery_id})"]

            case ActivityTypes.updateprofile:
                return [f"{self.actor_username}", "updated their profile.", f"Changed fields: {self.changed_fields}"]

            case ActivityTypes.removeprojectfromstudio:
                return [f"{self.actor_username}", "removed", f"-P {self.project_title} ({self.project_id})", "from",
                        f"-S {self.gallery_title} ({self.gallery_id})"]

            case ActivityTypes.addprojecttostudio:
                return [f"{self.actor_username}", "added", f"-P {self.project_title} ({self.project_id})", "to",
                        f"-S {self.gallery_title} ({self.gallery_id})"]

            case ActivityTypes.performaction:
                return [f"{self.actor_username}", "performed an action"]

            case _:
                raise NotImplementedError(
                    f"Activity type {self.type!r} is not implemented!\n"
                    f"{self.raw=}\n"
                    f"Raise an issue on github: https://github.com/TimMcCool/scratchattach/issues")

    def update(self):
        print("Warning: Activity objects can't be updated")
        return False  # Objects of this type cannot be updated

    def _update_from_dict(self, data: ActivityDict):
        self.raw = data

        self._session = data.get("_session", self._session)
        self.raw = data.get("raw", self.raw)

        self.id = data.get("id", self.id)
        self.actor_username = data.get("actor_username", self.actor_username)

        self.project_id = data.get("project_id", self.project_id)
        self.gallery_id = data.get("gallery_id", self.gallery_id)
        self.username = data.get("username", self.username)
        self.followed_username = data.get("followed_username", self.followed_username)
        self.recipient_username = data.get("recipient_username", self.recipient_username)
        self.title = data.get("title", self.title)
        self.project_title = data.get("project_title", self.project_title)
        self.gallery_title = data.get("gallery_title", self.gallery_title)
        self.topic_title = data.get("topic_title", self.topic_title)
        self.topic_id = data.get("topic_id", self.topic_id)
        self.target_name = data.get("target_name", self.target_name)
        self.target_id = data.get("target_id", self.target_id)

        self.parent_title = data.get("parent_title", self.parent_title)
        self.parent_id = data.get("parent_id", self.parent_id)

        self.comment_type = data.get("comment_type", self.comment_type)
        self.comment_obj_id = data.get("comment_obj_id", self.comment_obj_id)
        self.comment_obj_title = data.get("comment_obj_title", self.comment_obj_title)
        self.comment_id = data.get("comment_id", self.comment_id)
        self.comment_fragment = data.get("comment_fragment", self.comment_fragment)

        self.changed_fields = data.get("changed_fields", self.changed_fields)
        self.is_reshare = data.get("is_reshare", self.is_reshare)

        self.datetime_created_raw = data.get("datetime_created", self.datetime_created_raw)
        self.datetime_created = datetime.fromisoformat(self.datetime_created_raw)
        self.time = data.get("time", self.time)

        _type = data.get("type", self.type)
        if _type:
            self.type = ActivityTypes[_type]

        return True

    def _update_from_json(self, data: dict):
        """
        Update using JSON, used in the classroom API.
        """
        activity_type = data["type"]

        _time = data["datetime_created"] if "datetime_created" in data else None

        if "actor" in data:
            username = data["actor"]["username"]
        elif "actor_username" in data:
            username = data["actor_username"]
        else:
            username = None

        if recipient := data.get("recipient"):
            recipient_username = recipient["username"]
        elif recipient_username := data.get("recipient_username"):
            pass
        elif project_creator := data.get("project_creator"):
            recipient_username = project_creator["username"]
        else:
            recipient_username = None

        default_case = False
        # Even if `activity_type` is an invalid value; it will default to 'user performed an action'
        self.actor_username = username
        self.username = username
        self.raw = data
        self.datetime_created_raw = _time
        self.datetime_created = datetime.fromisoformat(self.datetime_created_raw)
        if activity_type == 0:
            self.type = ActivityTypes.followuser
            self.followed_username = data["followed_username"]

        elif activity_type == 1:
            self.type = ActivityTypes.followstudio
            self.gallery_id = data["gallery"]

        elif activity_type == 2:
            self.type = ActivityTypes.loveproject
            self.project_id = data["project"]
            self.recipient_username = recipient_username

        elif activity_type == 3:
            self.type = ActivityTypes.favoriteproject
            self.project_id = data["project"]
            self.recipient_username = recipient_username

        elif activity_type == 7:
            self.type = ActivityTypes.addprojecttostudio
            self.project_id = data["project"]
            self.gallery_id = data["gallery"]
            self.recipient_username = recipient_username

        elif activity_type in (8, 9, 10):
            self.type = ActivityTypes.shareproject
            self.is_reshare = data["is_reshare"]
            self.project_id = data["project"]
            self.recipient_username = recipient_username

        elif activity_type == 11:
            self.type = ActivityTypes.remixproject
            self.parent_id = data["parent"]
            warnings.warn(f"This may be incorrectly implemented.\n"
                          f"Raw data: {data}\n"
                          f"Please raise an issue on gh: https://github.com/TimMcCool/scratchattach/issues")
            self.recipient_username = recipient_username

        # type 12 does not exist in the HTML. That's why it was removed, not merged with type 13.

        elif activity_type == 13:
            self.type = ActivityTypes.createstudio
            self.gallery_id = data["gallery"]

        elif activity_type == 15:
            self.type = ActivityTypes.updatestudio
            self.gallery_id = data["gallery"]

        elif activity_type in (16, 17, 18, 19):
            self.type = ActivityTypes.removeprojectfromstudio
            self.gallery_id = data["gallery"]
            self.project_id = data["project"]

        elif activity_type in (20, 21, 22):
            self.type = ActivityTypes.promotetomanager
            self.recipient_username = recipient_username
            self.gallery_id = data["gallery"]

        elif activity_type in (23, 24, 25):
            self.type = ActivityTypes.updateprofile
            self.changed_fields = data.get("changed_fields", {})

        elif activity_type in (26, 27):
            # Comment in either project, user, or studio
            self.type = ActivityTypes.addcomment
            self.comment_fragment = data["comment_fragment"]
            self.comment_type = data["comment_type"]
            self.comment_obj_id = data["comment_obj_id"]
            self.comment_obj_title = data["comment_obj_title"]
            self.comment_id = data["comment_id"]

        else:
            # This is coded in the scratch HTML, haven't found an example of it though
            self.type = ActivityTypes.performaction


    def _update_from_html(self, data: Tag):

        self.raw = data

        _time = data.find('div').find('span').find_next().find_next().text.strip()

        if '\xa0' in _time:
            while '\xa0' in _time:
                _time = _time.replace('\xa0', ' ')

        self.datetime_created_raw = _time
        self.datetime_created = datetime.fromisoformat(self.datetime_created_raw)
        self.actor_username = data.find('div').find('span').text

        self.target_name = data.find('div').find('span').find_next().text
        self.target_link = data.find('div').find('span').find_next()["href"]
        # note that target_id can also be a username, so it isn't exclusively an int
        self.target_id = data.find('div').find('span').find_next()["href"].split("/")[-2]

        _type = data.find('div').find_all('span')[0].next_sibling.strip()
        if _type == "loved":
            self.type = ActivityTypes.loveproject

        elif _type == "favorited":
            self.type = ActivityTypes.favoriteproject

        elif "curator" in _type:
            self.type = ActivityTypes.becomecurator

        elif "shared" in _type:
            self.type = ActivityTypes.shareproject

        elif "is now following" in _type:
            if "users" in self.target_link:
                self.type = ActivityTypes.followuser
            else:
                self.type = ActivityTypes.followstudio

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
        _type = self.type.value

        if "project" in _type:  # target is a project
            if self.target_id:
                return self._make_linked_object("id", self.target_id, project.Project, exceptions.ProjectNotFound)
            if self.project_id:
                return self._make_linked_object("id", self.project_id, project.Project, exceptions.ProjectNotFound)

        if _type == "becomecurator" or _type == "followstudio":  # target is a studio
            if self.target_id:
                return self._make_linked_object("id", self.target_id, studio.Studio, exceptions.StudioNotFound)
            if self.gallery_id:
                return self._make_linked_object("id", self.gallery_id, studio.Studio, exceptions.StudioNotFound)
            # NOTE: the "becomecurator" type is ambigous - if it is inside the studio activity tab, the target is the user who joined
            if self.username:
                return self._make_linked_object("username", self.username, user.User, exceptions.UserNotFound)

        if _type == "followuser" or "curator" in _type:  # target is a user
            if self.target_name:
                return self._make_linked_object("username", self.target_name, user.User, exceptions.UserNotFound)
            if self.followed_username:
                return self._make_linked_object("username", self.followed_username, user.User, exceptions.UserNotFound)

        if self.recipient_username:  # the recipient_username field always indicates the target is a user
            return self._make_linked_object("username", self.recipient_username, user.User, exceptions.UserNotFound)

        if _type == "addcomment":  # target is a comment
            if self.comment_type == 0:
                # we need author name, but it has not been saved in this object
                _proj = self._session.connect_project(self.comment_obj_id)
                _c = _proj.comment_by_id(self.comment_id)

            elif self.comment_type == 1:
                _c = user.User(username=self.comment_obj_title, _session=self._session).comment_by_id(self.comment_id)
            elif self.comment_type == 2:
                _c = user.User(id=self.comment_obj_id, _session=self._session).comment_by_id(self.comment_id)
            else:
                raise ValueError(f"{self.comment_type} is an invalid comment type")

            return _c

        if _type == "forumpost":
            return forum.ForumTopic(id=603418, _session=self._session, title=self.title)

        return None
