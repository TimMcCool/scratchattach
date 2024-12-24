"""Activity and CloudActivity class"""
from __future__ import annotations

from bs4 import PageElement

from . import user, project, studio
from ._base import BaseSiteComponent
from ..utils import exceptions


class Activity(BaseSiteComponent):
    """
    Represents a Scratch activity (message or other user page activity)
    """

    def __repr__(self):
        return repr(self.raw)

    def str(self):
        return str(self.raw)

    def __init__(self, **entries):

        # Set attributes every Activity object needs to have:
        self._session = None
        self.raw = None

        # Possible attributes
        self.project_id = None
        self.gallery_id = None

        self.username = None
        self.followed_username = None
        self.recipient_username = None

        self.comment_type = None
        self.comment_obj_id = None
        self.comment_obj_title = None
        self.comment_id = None

        self.datetime_created = None
        self.time = None
        self.type = None

        # Update attributes from entries dict:
        self.__dict__.update(entries)

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
        """Whether this is 'blank'; it will default to 'user performed an action'"""
        if activity_type == 0:
            # follow
            followed_username = data["followed_username"]

            self.raw = f"{username} followed user {followed_username}"

            self.datetime_created = _time
            self.type = "followuser"
            self.username = username
            self.followed_username = followed_username

        elif activity_type == 1:
            # follow studio
            studio_id = data["gallery"]

            raw = f"{username} followed studio https://scratch.mit.edu/studios/{studio_id}"

            self.raw = raw
            self.datetime_created = _time
            self.type = "followstudio"

            self.username = username
            self.gallery_id = studio_id

        elif activity_type == 2:
            # love project
            project_id = data["project"]

            raw = f"{username} loved project https://scratch.mit.edu/projects/{project_id}"

            self.raw = raw
            self.datetime_created = _time,
            self.type = "loveproject"

            self.username = username
            self.project_id = project_id
            self.recipient_username = recipient_username

        elif activity_type == 3:
            # Favorite project
            project_id = data["project"]

            raw = f"{username} favorited project https://scratch.mit.edu/projects/{project_id}"

            self.raw = raw
            self.datetime_created = _time
            self.type = "favoriteproject"

            self.username = username
            self.project_id = project_id
            self.recipient_username = recipient_username

        elif activity_type == 7:
            # Add project to studio

            project_id = data["project"]
            studio_id = data["gallery"]

            raw = f"{username} added the project https://scratch.mit.edu/projects/{project_id} to studio https://scratch.mit.edu/studios/{studio_id}"

            self.raw = raw
            self.datetime_created = _time
            self.type = "addprojecttostudio"

            self.username = username
            self.project_id = project_id
            self.recipient_username = recipient_username

        elif activity_type == 8:
            default_case = True

        elif activity_type == 9:
            default_case = True

        elif activity_type == 10:
            # Share/Reshare project
            project_id = data["project"]
            is_reshare = data["is_reshare"]

            raw_reshare = "reshared" if is_reshare else "shared"

            raw = f"{username} {raw_reshare} the project https://scratch.mit.edu/projects/{project_id}"

            self.raw = raw
            self.datetime_created = _time
            self.type = "shareproject"

            self.username = username
            self.project_id = project_id
            self.recipient_username = recipient_username

        elif activity_type == 11:
            # Remix
            parent_id = data["parent"]

            raw = f"{username} remixed the project https://scratch.mit.edu/projects/{parent_id}"

            self.raw = raw
            self.datetime_created = _time
            self.type = "remixproject"

            self.username = username
            self.project_id = parent_id
            self.recipient_username = recipient_username

        elif activity_type == 12:
            default_case = True

        elif activity_type == 13:
            # Create ('add') studio
            studio_id = data["gallery"]

            raw = f"{username} created the studio https://scratch.mit.edu/studios/{studio_id}"

            self.raw = raw
            self.datetime_created = _time
            self.type = "createstudio"

            self.username = username
            self.gallery_id = studio_id

        elif activity_type == 15:
            # Update studio
            studio_id = data["gallery"]

            raw = f"{username} updated the studio https://scratch.mit.edu/studios/{studio_id}"

            self.raw = raw
            self.datetime_created = _time
            self.type = "updatestudio"

            self.username = username
            self.gallery_id = studio_id

        elif activity_type == 16:
            default_case = True

        elif activity_type == 17:
            default_case = True

        elif activity_type == 18:
            default_case = True

        elif activity_type == 19:
            # Remove project from studio

            project_id = data["project"]
            studio_id = data["gallery"]

            raw = f"{username} removed the project https://scratch.mit.edu/projects/{project_id} from studio https://scratch.mit.edu/studios/{studio_id}"

            self.raw = raw
            self.datetime_created = _time
            self.type = "removeprojectfromstudio"

            self.username = username
            self.project_id = project_id

        elif activity_type == 20:
            default_case = True

        elif activity_type == 21:
            default_case = True

        elif activity_type == 22:
            # Was promoted to manager for studio
            studio_id = data["gallery"]

            raw = f"{recipient_username} was promoted to manager by {username} for studio https://scratch.mit.edu/studios/{studio_id}"

            self.raw = raw
            self.datetime_created = _time
            self.type = "promotetomanager"

            self.username = username
            self.recipient_username = recipient_username
            self.gallery_id = studio_id

        elif activity_type == 23:
            default_case = True

        elif activity_type == 24:
            default_case = True

        elif activity_type == 25:
            # Update profile
            raw = f"{username} made a profile update"

            self.raw = raw
            self.datetime_created = _time
            self.type = "updateprofile"

            self.username = username

        elif activity_type == 26:
            default_case = True

        elif activity_type == 27:
            # Comment (quite complicated)
            comment_type: int = data["comment_type"]
            fragment = data["comment_fragment"]
            comment_id = data["comment_id"]
            comment_obj_id = data["comment_obj_id"]
            comment_obj_title = data["comment_obj_title"]

            if comment_type == 0:
                # Project comment
                raw = f"{username} commented on project https://scratch.mit.edu/projects/{comment_obj_id}/#comments-{comment_id} {fragment!r}"

            elif comment_type == 1:
                # Profile comment
                raw = f"{username} commented on user https://scratch.mit.edu/users/{comment_obj_title}/#comments-{comment_id} {fragment!r}"

            elif comment_type == 2:
                # Studio comment
                # Scratch actually provides an incorrect link, but it is fixed here:
                raw = f"{username} commented on studio https://scratch.mit.edu/studios/{comment_obj_id}/comments/#comments-{comment_id} {fragment!r}"

            else:
                raw = f"{username} commented {fragment!r}"  # This should never happen

            self.raw = raw
            self.datetime_created = _time
            self.type = "addcomment"

            self.username = username

            self.comment_type = comment_type
            self.comment_obj_id = comment_obj_id
            self.comment_obj_title = comment_obj_title
            self.comment_id = comment_id

        else:
            default_case = True

        if default_case:
            # This is coded in the scratch HTML, haven't found an example of it though
            raw = f"{username} performed an action"

            self.raw = raw
            self.datetime_created = _time
            self.type = "performaction"

            self.username = username

    def _update_from_html(self, data: PageElement):

        self.raw = data

        _time = data.find('div').find('span').findNext().findNext().text.strip()

        if '\xa0' in _time:
            while '\xa0' in _time:
                _time = _time.replace('\xa0', ' ')

        self.datetime_created = _time
        self.actor_username = data.find('div').find('span').text

        self.target_name = data.find('div').find('span').findNext().text
        self.target_link = data.find('div').find('span').findNext()["href"]
        self.target_id = data.find('div').find('span').findNext()["href"].split("/")[-2]

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
            if "target_id" in self.__dict__:
                return self._make_linked_object("id", self.target_id, project.Project, exceptions.ProjectNotFound)
            if "project_id" in self.__dict__:
                return self._make_linked_object("id", self.project_id, project.Project, exceptions.ProjectNotFound)

        if self.type == "becomecurator" or self.type == "followstudio":  # target is a studio
            if "target_id" in self.__dict__:
                return self._make_linked_object("id", self.target_id, studio.Studio, exceptions.StudioNotFound)
            if "gallery_id" in self.__dict__:
                return self._make_linked_object("id", self.gallery_id, studio.Studio, exceptions.StudioNotFound)
            # NOTE: the "becomecurator" type is ambigous - if it is inside the studio activity tab, the target is the user who joined
            if "username" in self.__dict__:
                return self._make_linked_object("username", self.username, user.User, exceptions.UserNotFound)

        if self.type == "followuser" or "curator" in self.type:  # target is a user
            if "target_name" in self.__dict__:
                return self._make_linked_object("username", self.target_name, user.User, exceptions.UserNotFound)
            if "followed_username" in self.__dict__:
                return self._make_linked_object("username", self.followed_username, user.User, exceptions.UserNotFound)
        if "recipient_username" in self.__dict__:  # the recipient_username field always indicates the target is a user
            return self._make_linked_object("username", self.recipient_username, user.User, exceptions.UserNotFound)

        if self.type == "addcomment":  # target is a comment
            if self.comment_type == 0:
                _c = project.Project(id=self.comment_obj_id, author_name=self._session.username,
                                     _session=self._session).comment_by_id(self.comment_id)
            if self.comment_type == 1:
                _c = user.User(username=self.comment_obj_title, _session=self._session).comment_by_id(self.comment_id)
            if self.comment_type == 2:
                _c = user.User(id=self.comment_obj_id, _session=self._session).comment_by_id(self.comment_id)
            else:
                raise ValueError(f"{self.comment_type} is an invalid comment type")

            return _c
