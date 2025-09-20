"""Activity and CloudActivity class"""
from __future__ import annotations

import html

from typing import Optional

from bs4 import Tag
from dataclasses import dataclass

from . import user, project, studio, session, forum
from ._base import BaseSiteComponent
from scratchattach.utils import exceptions


@dataclass
class Activity(BaseSiteComponent):
    """
    Represents a Scratch activity (message or other user page activity)
    """
    _session: Optional[session.Session] = None
    raw = None

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
    target_id: Optional[int] = None

    parent_title: Optional[str] = None
    parent_id: Optional[int] = None

    comment_type: Optional[int] = None
    comment_obj_id = None
    comment_obj_title: Optional[str] = None
    comment_id: Optional[int] = None
    comment_fragment: Optional[str] = None

    changed_fields: Optional[dict[str, str]] = None
    is_reshare: Optional[bool] = None

    datetime_created: Optional[str] = None
    time = None
    type = None

    def __repr__(self):
        return f"Activity({repr(self.raw)})"

    def __str__(self):
        return '-A ' +' '.join(self.parts)

    @property
    def parts(self):
        """
        Return format: [actor username] + N * [action, object]
        :return: A list of parts of the message. Join the parts to get a readable version, which is done with str(activity)
        """
        match self.type:
            case "loveproject":
                return [f"{self.actor_username}", "loved", f"-P {self.title!r} ({self.project_id})"]
            case "favoriteproject":
                return [f"{self.actor_username}", "favorited", f"-P {self.project_title!r} ({self.project_id})"]
            case "becomecurator":
                return [f"{self.actor_username}", "now curating", f"-S {self.title!r} ({self.gallery_id})"]
            case "followuser":
                return [f"{self.actor_username}", "followed", f"-U {self.followed_username}"]
            case "followstudio":
                return [f"{self.actor_username}", "followed", f"-S {self.title!r} ({self.gallery_id})"]
            case "shareproject":
                return [f"{self.actor_username}", "reshared" if self.is_reshare else "shared", f"-P {self.title!r} ({self.project_id})"]
            case "remixproject":
                return [f"{self.actor_username}", "remixed",
                        f"-P {self.parent_title!r} ({self.parent_id}) as -P {self.title!r} ({self.project_id})"]
            case "becomeownerstudio":
                return [f"{self.actor_username}", "became owner of", f"-S {self.gallery_title!r} ({self.gallery_id})"]

            case "addcomment":
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

            case "curatorinvite":
                return [f"{self.actor_username}", "invited you to curate", f"-S {self.title!r} ({self.gallery_id})"]

            case "userjoin":
                # This is also the first message you get - 'Welcome to Scratch'
                return [f"{self.actor_username}", "joined Scratch"]

            case "studioactivity":
                # the actor username should be systemuser
                return [f"{self.actor_username}", 'Studio activity', '', f"-S {self.title!r} ({self.gallery_id})"]

            case "forumpost":
                return [f"{self.actor_username}", "posted in", f"-F {self.topic_title} ({self.topic_id})"]

            case "updatestudio":
                return [f"{self.actor_username}", "updated", f"-S {self.gallery_title} ({self.gallery_id})"]

            case "createstudio":
                return [f"{self.actor_username}", "created", f"-S {self.gallery_title} ({self.gallery_id})"]

            case "promotetomanager":
                return [f"{self.actor_username}", "promoted", f"-U {self.recipient_username}", "in", f"-S {self.gallery_title} ({self.gallery_id})"]

            case "updateprofile":
                return [f"{self.actor_username}", "updated their profile.", f"Changed fields: {self.changed_fields}"]

            case "removeprojectfromstudio":
                return [f"{self.actor_username}", "removed", f"-P {self.project_title} ({self.project_id})", "from", f"-S {self.gallery_title} ({self.gallery_id})"]

            case "addprojecttostudio":
                return [f"{self.actor_username}", "added", f"-P {self.project_title} ({self.project_id})", "to", f"-S {self.gallery_title} ({self.gallery_id})"]

            case "performaction":
                return [f"{self.actor_username}", "performed an action"]

            case _:
                raise NotImplementedError(
                    f"Activity type {self.type!r} is not implemented!\n"
                    f"{self.raw=}\n"
                    f"Raise an issue on github: https://github.com/TimMcCool/scratchattach/issues")

    def update(self):
        print("Warning: Activity objects can't be updated")
        return False  # Objects of this type cannot be updated

    def _update_from_dict(self, data):
        self.raw = data
        self.__dict__.update(data)
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

        if data.get("recipient") is not None:
            recipient_username = data["recipient"]["username"]

        elif data.get("recipient_username") is not None:
            recipient_username = data["recipient_username"]

        elif data.get("project_creator") is not None:
            recipient_username = data["project_creator"]["username"]
        else:
            recipient_username = None

        default_case = False
        # Even if `activity_type` is an invalid value; it will default to 'user performed an action'

        self.raw = data
        if activity_type == 0:
            # follow
            followed_username = data["followed_username"]

            self.datetime_created = _time
            self.type = "followuser"
            self.username = username
            self.followed_username = followed_username

        elif activity_type == 1:
            # follow studio
            studio_id = data["gallery"]

            self.datetime_created = _time
            self.type = "followstudio"

            self.username = username
            self.gallery_id = studio_id

        elif activity_type == 2:
            # love project
            project_id = data["project"]

            self.datetime_created = _time
            self.type = "loveproject"

            self.username = username
            self.project_id = project_id
            self.recipient_username = recipient_username

        elif activity_type == 3:
            # Favorite project
            project_id = data["project"]

            self.datetime_created = _time
            self.type = "favoriteproject"

            self.username = username
            self.project_id = project_id
            self.recipient_username = recipient_username

        elif activity_type == 7:
            # Add project to studio

            project_id = data["project"]
            studio_id = data["gallery"]

            self.datetime_created = _time
            self.type = "addprojecttostudio"

            self.username = username
            self.gallery_id = studio_id
            self.project_id = project_id
            self.recipient_username = recipient_username

        elif activity_type in (8, 9, 10):
            # Share/Reshare project
            project_id = data["project"]
            is_reshare = data["is_reshare"]

            self.is_reshare = is_reshare
            self.datetime_created = _time
            self.type = "shareproject"

            self.username = username
            self.project_id = project_id
            self.recipient_username = recipient_username

        elif activity_type == 11:
            # Remix
            parent_id = data["parent"]

            self.datetime_created = _time
            self.type = "remixproject"

            self.username = username
            self.project_id = parent_id
            self.recipient_username = recipient_username

        # type 12 does not exist in the HTML. That's why it was removed, not merged with type 13.

        elif activity_type == 13:
            # Create ('add') studio
            studio_id = data["gallery"]

            self.datetime_created = _time
            self.type = "createstudio"

            self.username = username
            self.gallery_id = studio_id

        elif activity_type == 15:
            # Update studio
            studio_id = data["gallery"]

            self.datetime_created = _time
            self.type = "updatestudio"

            self.username = username
            self.gallery_id = studio_id

        elif activity_type in (16, 17, 18, 19):
            # Remove project from studio

            project_id = data["project"]
            studio_id = data["gallery"]

            self.datetime_created = _time
            self.type = "removeprojectfromstudio"
            self.gallery_id = studio_id
            self.project_id = project_id

            self.username = username
            self.project_id = project_id

        elif activity_type in (20, 21, 22):
            # Was promoted to manager for studio
            studio_id = data["gallery"]

            self.datetime_created = _time
            self.type = "promotetomanager"

            self.username = username
            self.recipient_username = recipient_username
            self.gallery_id = studio_id

        elif activity_type in (23, 24, 25):
            # Update profile
            self.datetime_created = _time
            self.type = "updateprofile"
            self.changed_fields = data.get("changed_fields", {})

            self.username = username

        elif activity_type in (26, 27):
            # Comment in either project, user, or studio
            comment_type: int = data["comment_type"]
            fragment = data["comment_fragment"]
            comment_id = data["comment_id"]
            comment_obj_id = data["comment_obj_id"]
            comment_obj_title = data["comment_obj_title"]

            self.datetime_created = _time
            self.type = "addcomment"

            self.username = username

            self.comment_fragment = fragment
            self.comment_type = comment_type
            self.comment_obj_id = comment_obj_id
            self.comment_obj_title = comment_obj_title
            self.comment_id = comment_id
        else:
            default_case = True

        if default_case:
            # This is coded in the scratch HTML, haven't found an example of it though
            self.datetime_created = _time
            self.type = "performaction"

            self.username = username

        if not self.actor_username:
            self.actor_username = self.username

    def _update_from_html(self, data: Tag):

        self.raw = data

        _time = data.find('div').find('span').find_next().find_next().text.strip()

        if '\xa0' in _time:
            while '\xa0' in _time:
                _time = _time.replace('\xa0', ' ')

        self.datetime_created = _time
        self.actor_username = data.find('div').find('span').text

        self.target_name = data.find('div').find('span').find_next().text
        self.target_link = data.find('div').find('span').find_next()["href"]
        self.target_id = data.find('div').find('span').find_next()["href"].split("/")[-2]

        self.type = data.find('div').find_all('span')[0].next_sibling.strip()
        if self.type == "loved":
            self.type = "loveproject"

        elif self.type == "favorited":
            self.type = "favoriteproject"

        elif "curator" in self.type:
            self.type = "becomecurator"

        elif "shared" in self.type:
            self.type = "shareproject"

        elif "is now following" in self.type:
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

        if "project" in self.type:  # target is a project
            if self.target_id:
                return self._make_linked_object("id", self.target_id, project.Project, exceptions.ProjectNotFound)
            if self.project_id:
                return self._make_linked_object("id", self.project_id, project.Project, exceptions.ProjectNotFound)

        if self.type == "becomecurator" or self.type == "followstudio":  # target is a studio
            if self.target_id:
                return self._make_linked_object("id", self.target_id, studio.Studio, exceptions.StudioNotFound)
            if self.gallery_id:
                return self._make_linked_object("id", self.gallery_id, studio.Studio, exceptions.StudioNotFound)
            # NOTE: the "becomecurator" type is ambigous - if it is inside the studio activity tab, the target is the user who joined
            if self.username:
                return self._make_linked_object("username", self.username, user.User, exceptions.UserNotFound)

        if self.type == "followuser" or "curator" in self.type:  # target is a user
            if self.target_name:
                return self._make_linked_object("username", self.target_name, user.User, exceptions.UserNotFound)
            if self.followed_username:
                return self._make_linked_object("username", self.followed_username, user.User, exceptions.UserNotFound)

        if self.recipient_username:  # the recipient_username field always indicates the target is a user
            return self._make_linked_object("username", self.recipient_username, user.User, exceptions.UserNotFound)

        if self.type == "addcomment":  # target is a comment
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

        if self.type == "forumpost":
            return forum.ForumTopic(id=603418, _session=self._session, title=self.title)

        return None
