"""Studio class"""
from __future__ import annotations

import json
import random
from . import user, comment, project, activity
from ..utils import exceptions, commons
from ..utils.commons import api_iterative, headers
from ._base import BaseSiteComponent

from ..utils.requests import Requests as requests


class Studio(BaseSiteComponent):
    """
    Represents a Scratch studio.

    Attributes:

    :.id:

    :.title:

    :.description:

    :.host_id: The user id of the studio host

    :.open_to_all: Whether everyone is allowed to add projects

    :.comments_allowed:

    :.image_url:

    :.created:

    :.modified:

    :.follower_count:

    :.manager_count:

    :.project_count:

    :.update(): Updates the attributes

    """

    def __init__(self, **entries):

        # Info on how the .update method has to fetch the data:
        self.update_function = requests.get
        self.update_API = f"https://api.scratch.mit.edu/studios/{entries['id']}"

        # Set attributes every Project object needs to have:
        self._session = None
        self.id = 0

        # Update attributes from entries dict:
        self.__dict__.update(entries)

        # Headers and cookies:
        if self._session is None:
            self._headers = headers
            self._cookies = {}
        else:
            self._headers = self._session._headers
            self._cookies = self._session._cookies

        # Headers for operations that require accept and Content-Type fields:
        self._json_headers = dict(self._headers)
        self._json_headers["accept"] = "application/json"
        self._json_headers["Content-Type"] = "application/json"

    def _update_from_dict(self, studio):
        try: self.id = int(studio["id"])
        except Exception: pass
        try: self.title = studio["title"]
        except Exception: pass
        try: self.description = studio["description"]
        except Exception: pass
        try: self.host_id = studio["host"]
        except Exception: pass
        try: self.open_to_all = studio["open_to_all"]
        except Exception: pass
        try: self.comments_allowed = studio["comments_allowed"]
        except Exception: pass
        try: self.image_url = studio["image"]
        except Exception: pass
        try: self.created = studio["history"]["created"]
        except Exception: pass
        try: self.modified = studio["history"]["modified"]
        except Exception: pass
        try: self.follower_count = studio["stats"]["followers"]
        except Exception: pass
        try: self.manager_count = studio["stats"]["managers"]
        except Exception: pass
        try: self.project_count = studio["stats"]["projects"]
        except Exception: pass
        return True

    def follow(self):
        """
        You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_studio`
        """
        self._assert_auth()
        requests.put(
            f"https://scratch.mit.edu/site-api/users/bookmarkers/{self.id}/add/?usernames={self._session._username}",
            headers=headers,
            cookies=self._cookies,
            timeout=10,
        )

    def unfollow(self):
        """
        You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_studio`
        """
        self._assert_auth()
        requests.put(
            f"https://scratch.mit.edu/site-api/users/bookmarkers/{self.id}/remove/?usernames={self._session._username}",
            headers=headers,
            cookies=self._cookies,
            timeout=10,
        )

    def comments(self, *, limit=40, offset=0) -> list[comment.Comment]:
        """
        Returns the comments posted on the studio (except for replies. To get replies use :meth:`scratchattach.studio.Studio.get_comment_replies`).

        Keyword Arguments:
            page: The page of the comments that should be returned.
            limit: Max. amount of returned comments.

        Returns:
            list<Comment>: A list containing the requested comments as Comment objects.
        """
        response = commons.api_iterative(
            f"https://api.scratch.mit.edu/studios/{self.id}/comments/", limit=limit, offset=offset, add_params=f"&cachebust={random.randint(0,9999)}")
        for i in response:
            i["source"] = "studio"
            i["source_id"] = self.id
        return commons.parse_object_list(response, comment.Comment, self._session)

    def comment_replies(self, *, comment_id, limit=40, offset=0) -> list[comment.Comment]:
        response = commons.api_iterative(
            f"https://api.scratch.mit.edu/studios/{self.id}/comments/{comment_id}/replies", limit=limit, offset=offset, add_params=f"&cachebust={random.randint(0,9999)}")
        for x in response:
            x["parent_id"] = comment_id    
            x["source"] = "studio"
            x["source_id"] = self.id    
        return commons.parse_object_list(response, comment.Comment, self._session)

    def comment_by_id(self, comment_id):
        r = requests.get(
            f"https://api.scratch.mit.edu/studios/{self.id}/comments/{comment_id}",
            timeout=10,
        ).json()
        if r is None:
            raise exceptions.CommentNotFound()
        _comment = comment.Comment(id=r["id"], _session=self._session, source="studio", source_id=self.id)
        _comment._update_from_dict(r)
        return _comment

    def post_comment(self, content, *, parent_id="", commentee_id=""):
        """
        Posts a comment on the studio. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_studio`

        Args:
            content: Content of the comment that should be posted

        Keyword Arguments:
            parent_id: ID of the comment you want to reply to. If you don't want to mention a user, don't put the argument.
            commentee_id: ID of the user that will be mentioned in your comment and will receive a message about your comment. If you don't want to mention a user, don't put the argument.
        
        Returns:
            scratchattach.comment.Comment: The posted comment as Comment object.
        """
        self._assert_auth()
        data = {
            "commentee_id": commentee_id,
            "content": str(content),
            "parent_id": parent_id,
        }
        headers = dict(self._json_headers)
        headers["referer"] = "https://scratch.mit.edu/projects/" + str(self.id) + "/"
        r = requests.post(
            f"https://api.scratch.mit.edu/proxy/comments/studio/{self.id}/",
            headers=headers,
            cookies=self._cookies,
            data=json.dumps(data),
            timeout=10,
        ).json()
        if "id" not in r:
            raise exceptions.CommentPostFailure(r)
        _comment = comment.Comment(id=r["id"], _session=self._session, source="studio", source_id=self.id)
        _comment._update_from_dict(r)
        return _comment

    def delete_comment(self, *, comment_id):
        # NEEDS TO BE TESTED!
        """
        Deletes a comment by ID. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_project`

        Args:
            comment_id: The id of the comment that should be deleted
        """
        self._assert_auth()
        return requests.delete(
            f"https://api.scratch.mit.edu/proxy/comments/studio/{self.id}/comment/{comment_id}/",
            headers=self._headers,
            cookies=self._cookies,
        ).headers

    def report_comment(self, *, comment_id):
        # NEEDS TO BE TESTED!
        """
        Reports a comment by ID to the Scratch team. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_project`

        Args:
            comment_id: The id of the comment that should be reported
        """
        self._assert_auth()
        return requests.delete(
            f"https://api.scratch.mit.edu/proxy/comments/studio/{self.id}/comment/{comment_id}/report",
            headers=self._headers,
            cookies=self._cookies,
        )

    def set_thumbnail(self, *, file):
        """
        Sets the studio thumbnail. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_studio`

        Keyword Arguments:
            file: The path to the image file

        Returns:
            str: Scratch cdn link to the set thumbnail
        """
        self._assert_auth()
        with open(file, "rb") as f:
            thumbnail = f.read()

        filename = file.replace("\\", "/")
        if filename.endswith("/"):
            filename = filename[:-1]
        filename = filename.split("/").pop()

        file_type = filename.split(".").pop()

        payload1 = f'------WebKitFormBoundaryhKZwFjoxAyUTMlSh\r\nContent-Disposition: form-data; name="file"; filename="{filename}"\r\nContent-Type: image/{file_type}\r\n\r\n'
        payload1 = payload1.encode("utf-8")
        payload2 = b"\r\n------WebKitFormBoundaryhKZwFjoxAyUTMlSh--\r\n"
        payload = b"".join([payload1, thumbnail, payload2])

        r = requests.post(
            f"https://scratch.mit.edu/site-api/galleries/all/{self.id}/",
            headers={
                "accept": "*/",
                "content-type": "multipart/form-data; boundary=----WebKitFormBoundaryhKZwFjoxAyUTMlSh",
                "Referer": "https://scratch.mit.edu/",
                "x-csrftoken": "a",
                "x-requested-with": "XMLHttpRequest",
            },
            data=payload,
            cookies=self._cookies,
            timeout=10,
        ).json()

        if "errors" in r:
            raise (exceptions.BadRequest(", ".join(r["errors"])))
        else:
            return r["thumbnail_url"]

    def reply_comment(self, content, *, parent_id, commentee_id=""):
        """
        Posts a reply to a comment on the studio. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_studio`

        Args:
            content: Content of the comment that should be posted

        Warning:
            Only replies to top-level comments are shown on the Scratch website. Replies to replies are actually replies to the corresponding top-level comment in the API.
            
            Therefore, parent_id should be the comment id of a top level comment.

        Keyword Arguments:
            parent_id: ID of the comment you want to reply to
            commentee_id: ID of the user you are replying to
        """
        self._assert_auth()
        return self.post_comment(
            content, parent_id=parent_id, commentee_id=commentee_id
        )

    def projects(self, limit=40, offset=0):
        """
        Gets the studio projects.

        Keyword arguments:
            limit (int): Max amount of returned projects.
            offset (int): Offset of the first returned project.

        Returns:
            list<scratchattach.project.Project>: A list containing the studio projects as Project objects
        """
        response = commons.api_iterative(
            f"https://api.scratch.mit.edu/studios/{self.id}/projects", limit=limit, offset=offset)
        return commons.parse_object_list(response, project.Project, self._session)

    def curators(self, limit=40, offset=0):
        """
        Gets the studio curators.

        Keyword arguments:
            limit (int): Max amount of returned curators.
            offset (int): Offset of the first returned curator.

        Returns:
            list<scratchattach.user.User>: A list containing the studio curators as User objects
        """
        response = commons.api_iterative(
            f"https://api.scratch.mit.edu/studios/{self.id}/curators", limit=limit, offset=offset)
        return commons.parse_object_list(response, user.User, self._session, "username")


    def invite_curator(self, curator):
        """
        You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_studio`
        """
        self._assert_auth()
        try:
            return requests.put(
                f"https://scratch.mit.edu/site-api/users/curators-in/{self.id}/invite_curator/?usernames={curator}",
                headers=headers,
                cookies=self._cookies,
                timeout=10,
            ).json()
        except Exception:
            raise (exceptions.Unauthorized)

    def promote_curator(self, curator):
        """
        You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_studio`
        """
        self._assert_auth()
        try:
            return requests.put(
                f"https://scratch.mit.edu/site-api/users/curators-in/{self.id}/promote/?usernames={curator}",
                headers=headers,
                cookies=self._cookies,
                timeout=10,
            ).json()
        except Exception:
            raise (exceptions.Unauthorized)

    def remove_curator(self, curator):
        """
        You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_studio`
        """
        self._assert_auth()
        try:
            return requests.put(
                f"https://scratch.mit.edu/site-api/users/curators-in/{self.id}/remove/?usernames={curator}",
                headers=headers,
                cookies=self._cookies,
                timeout=10,
            ).json()
        except Exception:
            raise (exceptions.Unauthorized)
    
    def transfer_ownership(self, new_owner, *, password):
        """
        Makes another Scratcher studio host. You need to specify your password to do this.
        
        Arguments:
            new_owner (str): Username of new host

        Keyword arguments:
            password (str): The password of your Scratch account
        
        Warning:
            This action is irreversible!
        """
        self._assert_auth()
        try:
            return requests.put(
                f"https://api.scratch.mit.edu/studios/{self.id}/transfer/{new_owner}",
                headers=self._headers,
                cookies=self._cookies,
                timeout=10,
                json={"password":password}
            ).json()
        except Exception:
            raise (exceptions.Unauthorized)
    

    def leave(self):
        """
        Removes yourself from the studio. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_studio`
        """
        self._assert_auth()
        return self.remove_curator(self._session._username)

    def add_project(self, project_id):
        """
        Adds a project to the studio. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_studio`

        Args:
            project_id: Project id of the project that should be added
        """
        self._assert_auth()
        return requests.post(
            f"https://api.scratch.mit.edu/studios/{self.id}/project/{project_id}",
            headers=self._headers,
            timeout=10,
        ).json()

    def remove_project(self, project_id):
        """
        Removes a project from the studio. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_studio`

        Args:
            project_id: Project id of the project that should be removed
        """
        self._assert_auth()
        return requests.delete(
            f"https://api.scratch.mit.edu/studios/{self.id}/project/{project_id}",
            headers=self._headers,
            timeout=10,
        ).json()

    def managers(self, limit=40, offset=0):
        """
        Gets the studio managers.

        Keyword arguments:
            limit (int): Max amount of returned managers
            offset (int): Offset of the first returned manager.

        Returns:
            list<scratchattach.user.User>: A list containing the studio managers as user objects
        """
        response = commons.api_iterative(
            f"https://api.scratch.mit.edu/studios/{self.id}/managers", limit=limit, offset=offset)
        return commons.parse_object_list(response, user.User, self._session, "username")

    def host(self):
        """
        Gets the studio host.

        Returns:
            scratchattach.user.User: An object representing the studio host.
        """
        managers = self.managers(limit=1, offset=0)
        try:
            return managers[0]
        except Exception:
            return None

    def set_fields(self, fields_dict):
        """
        Sets fields. Uses the scratch.mit.edu/site-api PUT API.
        """
        self._assert_auth()
        requests.put(
            f"https://scratch.mit.edu/site-api/galleries/all/{self.id}/",
            headers=headers,
            cookies=self._cookies,
            data=json.dumps(fields_dict),
            timeout=10,
        )


    def set_description(self, new):
        """
        You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_studio`
        """
        self.set_fields({"description": new + "\n"})

    def set_title(self, new):
        """
        You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_studio`
        """
        self.set_fields({"title": new})

    def open_projects(self):
        """
        Changes the studio settings so everyone (including non-curators) is able to add projects to the studio. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_studio`
        """
        self._assert_auth()
        requests.put(
            f"https://scratch.mit.edu/site-api/galleries/{self.id}/mark/open/",
            headers=headers,
            cookies=self._cookies,
            timeout=10,
        )

    def close_projects(self):
        """
        Changes the studio settings so only curators can add projects to the studio. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_studio`
        """
        self._assert_auth()
        requests.put(
            f"https://scratch.mit.edu/site-api/galleries/{self.id}/mark/closed/",
            headers=headers,
            cookies=self._cookies,
            timeout=10,
        )

    def turn_off_commenting(self):
        """
        You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_studio`
        """
        self._assert_auth()
        if self.comments_allowed:
            requests.post(
                f"https://scratch.mit.edu/site-api/comments/gallery/{self.id}/toggle-comments/",
                headers=headers,
                cookies=self._cookies,
                timeout=10,
            )
            self.comments_allowed = not self.comments_allowed

    def turn_on_commenting(self):
        """
        You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_studio`
        """
        self._assert_auth()
        if not self.comments_allowed:
            requests.post(
                f"https://scratch.mit.edu/site-api/comments/gallery/{self.id}/toggle-comments/",
                headers=headers,
                cookies=self._cookies,
                timeout=10,
            )
            self.comments_allowed = not self.comments_allowed

    def toggle_commenting(self):
        """
        You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_studio`
        """
        self._assert_auth()
        requests.post(
            f"https://scratch.mit.edu/site-api/comments/gallery/{self.id}/toggle-comments/",
            headers=headers,
            cookies=self._cookies,
            timeout=10,
        )
        self.comments_allowed = not self.comments_allowed

    def activity(self, *, limit=40, offset=0, date_limit=None):
        add_params = ""
        if date_limit is not None:
            add_params = f"&dateLimit={date_limit}"
        response = commons.api_iterative(
            f"https://api.scratch.mit.edu/studios/{self.id}/activity", limit=limit, offset=offset, add_params=add_params)
        return commons.parse_object_list(response, activity.Activity, self._session)

    def accept_invite(self):
        self._assert_auth()
        return requests.put(
            f"https://scratch.mit.edu/site-api/users/curators-in/{self.id}/add/?usernames={self._session._username}",
            headers=headers,
            cookies=self._cookies,
            timeout=10,
        ).json()
    
    def your_role(self):
        """
        Returns a dict with information about your role in the studio (whether you're following, curating, managing it or are invited)
        """
        self._assert_auth()
        return requests.get(
            f"https://api.scratch.mit.edu/studios/{self.id}/users/{self._session.username}",
            headers=self._headers,
            cookies=self._cookies,
            timeout=10,
        ).json()


def get_studio(studio_id) -> Studio:
    """
    Gets a studio without logging in.

    Args:
        studio_id (int): Studio id of the requested studio

    Returns:
        scratchattach.studio.Studio: An object representing the requested studio

    Warning:
        Any methods that authentication (like studio.follow) will not work on the returned object.

        If you want to use these, get the studio with :meth:`scratchattach.session.Session.connect_studio` instead.
    """
    print("Warning: For methods that require authentication, use session.connect_studio instead of get_studio")
    return commons._get_object("id", studio_id, Studio, exceptions.StudioNotFound)

def search_studios(*, query="", mode="trending", language="en", limit=40, offset=0):
    if not query:
        raise ValueError("The query can't be empty for search")
    response = commons.api_iterative(
        f"https://api.scratch.mit.edu/search/studios", limit=limit, offset=offset, add_params=f"&language={language}&mode={mode}&q={query}")
    return commons.parse_object_list(response, Studio)


def explore_studios(*, query="", mode="trending", language="en", limit=40, offset=0):
    if not query:
        raise ValueError("The query can't be empty for explore")
    response = commons.api_iterative(
        f"https://api.scratch.mit.edu/explore/studios", limit=limit, offset=offset, add_params=f"&language={language}&mode={mode}&q={query}")
    return commons.parse_object_list(response, Studio)
