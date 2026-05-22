"""Activity and CloudActivity class"""

from __future__ import annotations
import html
import warnings
from dataclasses import dataclass
from typing import Optional, Any
from enum import Enum
from bs4 import Tag
from . import user, project, studio, session, forum, comment
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
    comment_obj_id: Optional[int] = None
    comment_obj_title: Optional[str] = None
    comment_id: Optional[int] = None
    comment_fragment: Optional[str] = None
    changed_fields: Optional[dict[str, str]] = None
    is_reshare: Optional[bool] = None
    datetime_created: Optional[str] = None
    time: Any = None
    type: Optional[ActivityTypes] = None

    def __repr__(self):
        return f"Activity({repr(self.raw)})"

    def __str__(self):
        return "-A " + " ".join(self.parts)

    def _parts_simple(self, verb: str, obj: str):
        return [str(self.actor_username), verb, obj]

    def _parts_comment(self) -> list[str]:
        ret = [str(self.actor_username), "commented on"]
        if self.comment_type not in (0, 1, 2):
            raise ValueError(f"Unknown comment type: {self.comment_type}")
        ret.append(
            {
                0: f"-P {self.comment_obj_title!r} ({self.comment_obj_id}",
                1: f"-U {self.comment_obj_title}",
                2: f"-S {self.comment_obj_title!r} ({self.comment_obj_id}",
            }[self.comment_type]
        )
        ret[-1] += f"#{self.comment_id})"
        ret.append(str(html.unescape(str(self.comment_fragment))))
        return ret

    @property
    def parts(self):
        """
        Return format: [actor username] + N * [action, object]
        :return: A list of parts of the message. Join the parts to get a readable version, which is done with str(activity)
        """
        SIMPLE_SOLNS = {
            ActivityTypes.loveproject: ("loved", f"-P {self.title!r} ({self.project_id})"),
            ActivityTypes.favoriteproject: ("favorited", f"-P {self.project_title!r} ({self.project_id})"),
            ActivityTypes.becomecurator: ("now curating", f"-S {self.title!r} ({self.gallery_id})"),
            ActivityTypes.followuser: ("followed", f"-U {self.followed_username}"),
            ActivityTypes.followstudio: ("followed", f"-S {self.title!r} ({self.gallery_id})"),
            ActivityTypes.shareproject: (
                "reshared" if self.is_reshare else "shared",
                f"-P {self.title!r} ({self.project_id})",
            ),
            ActivityTypes.remixproject: (
                "remixed",
                f"-P {self.parent_title!r} ({self.parent_id}) as -P {self.title!r} ({self.project_id})",
            ),
            ActivityTypes.becomeownerstudio: ("became owner of", f"-S {self.gallery_title!r} ({self.gallery_id})"),
            ActivityTypes.curatorinvite: ("invited you to curate", f"-S {self.title!r} ({self.gallery_id})"),
            ActivityTypes.forumpost: ("posted in", f"-F {self.topic_title} ({self.topic_id})"),
            ActivityTypes.updatestudio: ("updated", f"-S {self.gallery_title} ({self.gallery_id})"),
            ActivityTypes.createstudio: ("created", f"-S {self.gallery_title} ({self.gallery_id})"),
            None: (),
        }
        if args := SIMPLE_SOLNS.get(self.type):
            return self._parts_simple(*args)
        match self.type:
            case ActivityTypes.addcomment:
                return self._parts_comment()
            case ActivityTypes.userjoin:
                return [str(self.actor_username), "joined Scratch"]
            case ActivityTypes.studioactivity:
                return [str(self.actor_username), "Studio activity", "", f"-S {self.title!r} ({self.gallery_id})"]
            case ActivityTypes.promotetomanager:
                return [
                    str(self.actor_username),
                    "promoted",
                    f"-U {self.recipient_username}",
                    "in",
                    f"-S {self.gallery_title} ({self.gallery_id})",
                ]
            case ActivityTypes.updateprofile:
                return [str(self.actor_username), "updated their profile.", f"Changed fields: {self.changed_fields}"]
            case ActivityTypes.removeprojectfromstudio:
                return [
                    f"{self.actor_username}",
                    "removed",
                    f"-P {self.project_title} ({self.project_id})",
                    "from",
                    f"-S {self.gallery_title} ({self.gallery_id})",
                ]
            case ActivityTypes.addprojecttostudio:
                return [
                    f"{self.actor_username}",
                    "added",
                    f"-P {self.project_title} ({self.project_id})",
                    "to",
                    f"-S {self.gallery_title} ({self.gallery_id})",
                ]
            case ActivityTypes.performaction:
                return [f"{self.actor_username}", "performed an action"]
            case _:
                raise NotImplementedError(
                    f"Activity type {self.type!r} is not implemented!\nself.raw={self.raw!r}\nRaise an issue on github: https://github.com/TimMcCool/scratchattach/issues"
                )

    def update(self):
        print("Warning: Activity objects can't be updated")
        return False

    def _update_from_data(self, data):
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
        self.datetime_created = data.get("datetime_created", self.datetime_created)
        self.time = data.get("time", self.time)
        _type = data.get("type", self.type)
        if _type == "becomehoststudio":
            self.type = ActivityTypes.becomeownerstudio
        elif _type:
            self.type = ActivityTypes[_type]
        return True

    def _update_from_json(self, data: dict):
        """
        Update using JSON, used in the classroom API.
        """
        activity_type = data["type"]
        _time = data.get("datetime_created")
        if "actor" in data:
            self.username = data["actor"]["username"]
        else:
            self.username = data.get("actor_username")
        self.recipient_username = None
        if recipient := data.get("recipient"):
            self.recipient_username = recipient["username"]
        elif ru := data.get("recipient_username"):
            self.recipient_username = ru
        elif project_creator := data.get("project_creator"):
            self.recipient_username = project_creator["username"]
        self.actor_username = self.username
        self.raw = data
        self.datetime_created = _time
        self.type = {
            0: ActivityTypes.followuser,
            1: ActivityTypes.followstudio,
            2: ActivityTypes.loveproject,
            3: ActivityTypes.favoriteproject,
            7: ActivityTypes.addprojecttostudio,
            8: ActivityTypes.shareproject,
            9: ActivityTypes.shareproject,
            10: ActivityTypes.shareproject,
            11: ActivityTypes.remixproject,
            13: ActivityTypes.createstudio,
            15: ActivityTypes.updatestudio,
            16: ActivityTypes.removeprojectfromstudio,
            17: ActivityTypes.removeprojectfromstudio,
            18: ActivityTypes.removeprojectfromstudio,
            19: ActivityTypes.removeprojectfromstudio,
            20: ActivityTypes.promotetomanager,
            21: ActivityTypes.promotetomanager,
            22: ActivityTypes.promotetomanager,
            23: ActivityTypes.updateprofile,
            24: ActivityTypes.updateprofile,
            25: ActivityTypes.updateprofile,
            26: ActivityTypes.addcomment,
            27: ActivityTypes.addcomment,
            None: ActivityTypes.performaction,
        }.get(activity_type, ActivityTypes.performaction)
        self.followed_username = data.get("followed_username", self.followed_username)
        self.gallery_id = data.get("gallery", self.gallery_id)
        self.project_id = data.get("project", self.project_id)
        self.is_reshare = data.get("is_reshare", self.is_reshare)
        self.comment_fragment = data.get("comment_fragment", self.comment_fragment)
        self.comment_type = data.get("comment_type", self.comment_type)
        self.comment_obj_id = data.get("comment_obj_id", self.comment_obj_id)
        self.comment_obj_title = data.get("comment_obj_title", self.comment_obj_title)
        self.comment_id = data.get("comment_id", self.comment_id)
        self.parent_id = data.get("parent", self.parent_id)
        if self.parent_id:
            warnings.warn(
                f"This may be incorrectly implemented.\nRaw data: {data}\nPlease raise an issue on gh: https://github.com/TimMcCool/scratchattach/issues"
            )
        if self.type == ActivityTypes.updateprofile:
            self.changed_fields = data.get("changed_fields", {})

    def _update_from_html(self, data: Tag):
        self.raw = data
        _time = data.find("div").find("span").find_next().find_next().text.strip()
        if "\xa0" in _time:
            while "\xa0" in _time:
                _time = _time.replace("\xa0", " ")
        self.datetime_created = _time
        self.actor_username = data.find("div").find("span").text
        self.target_name = data.find("div").find("span").find_next().text
        self.target_link = data.find("div").find("span").find_next()["href"]
        self.target_id = data.find("div").find("span").find_next()["href"].split("/")[-2]
        _type = data.find("div").find_all("span")[0].next_sibling.strip()
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

    def target_project(self) -> Optional[project.Project]:
        if self.target_id:
            return self._make_linked_object("id", self.target_id, project.Project, exceptions.ProjectNotFound)
        if self.project_id:
            return self._make_linked_object("id", self.project_id, project.Project, exceptions.ProjectNotFound)
        return None

    def target_studio(self) -> Optional[studio.Studio]:
        if self.target_id:
            return self._make_linked_object("id", self.target_id, studio.Studio, exceptions.StudioNotFound)
        if self.gallery_id:
            return self._make_linked_object("id", self.gallery_id, studio.Studio, exceptions.StudioNotFound)
        return None

    def target_user(self) -> Optional[user.User]:
        if self.username:
            return self._make_linked_object("username", self.username, user.User, exceptions.UserNotFound)
        if self.target_name:
            return self._make_linked_object("username", self.target_name, user.User, exceptions.UserNotFound)
        if self.followed_username:
            return self._make_linked_object("username", self.followed_username, user.User, exceptions.UserNotFound)
        if self.recipient_username:
            return self._make_linked_object("username", self.recipient_username, user.User, exceptions.UserNotFound)
        return None

    def target_comment(self) -> Optional[comment.Comment]:
        if self.comment_type == 0:
            if self.comment_obj_id is None:
                return None
            if self._session is not None:
                _proj = self._session.connect_project(self.comment_obj_id)
            else:
                _proj = project.Project(id=self.comment_obj_id)
            return _proj.comment_by_id(self.comment_id)
        elif self.comment_type == 1:
            return user.User(username=self.comment_obj_title, _session=self._session).comment_by_id(self.comment_id)
        elif self.comment_type == 2:
            return user.User(id=self.comment_obj_id, _session=self._session).comment_by_id(self.comment_id)
        else:
            return None

    def target(self):
        """
        Returns the activity's target (depending on the activity, this is either a User, Project, Studio or Comment object).
        May also return None if the activity type is unknown.
        """
        if self.type is None:
            return None
        _type = self.type.value
        if self.type in (
            ActivityTypes.addprojecttostudio,
            ActivityTypes.favoriteproject,
            ActivityTypes.loveproject,
            ActivityTypes.remixproject,
            ActivityTypes.removeprojectfromstudio,
            ActivityTypes.shareproject,
        ):
            return self.target_project()
        if self.type in (ActivityTypes.becomecurator, ActivityTypes.followstudio):
            if ret := self.target_studio():
                return ret
            return self.target_user()
        if self.type in (ActivityTypes.followuser, ActivityTypes.curatorinvite) or self.recipient_username:
            return self.target_user()
        if self.type == ActivityTypes.addcomment:
            if ret := self.target_comment():
                return ret
            raise ValueError(f"Either {self.comment_type} is an invalid comment type, or the linked target could not be found")
        if _type == "forumpost":
            return forum.ForumTopic(id=603418, _session=self._session, title=self.title)
        return None
