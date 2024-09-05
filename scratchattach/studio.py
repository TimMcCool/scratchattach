# ----- Getting studios

import json
import requests
import random
from . import user
from . import exceptions
from .commons import api_iterative_simple, headers


class Studio:
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
        self.__dict__.update(entries)

        if not hasattr(self, "_session"):
            self._session = None
        if self._session is None:
            self._headers = headers
            self._cookies = {}
        else:
            self._headers = self._session._headers
            self._cookies = self._session._cookies

        try:
            self._headers.pop("Cookie")
        except Exception:
            pass
        self._json_headers = self._headers
        self._json_headers["accept"] = "application/json"
        self._json_headers["Content-Type"] = "application/json"

    def update(self):
        """
        Updates the attributes of the Studio object
        """
        studio = requests.get(f"https://api.scratch.mit.edu/studios/{self.id}", timeout=10)
        if "429" in str(studio):
            return "429"
        if studio.text == '{\n  "response": "Too many requests"\n}':
            return "429"
        studio = studio.json()
        return self._update_from_dict(studio)

    def _update_from_dict(self, studio):
        self.id = int(studio["id"])
        self.title = studio["title"]
        self.description = studio["description"]
        self.host_id = studio["host"]
        self.open_to_all = studio["open_to_all"]
        self.comments_allowed = studio["comments_allowed"]
        self.image_url = studio["image"]
        self.created = studio["history"]["created"]
        self.modified = studio["history"]["modified"]
        self.follower_count = studio["stats"]["followers"]
        self.manager_count = studio["stats"]["managers"]
        self.project_count = studio["stats"]["projects"]

    def follow(self):
        """
        You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_studio`
        """
        if self._session is None:
            raise (exceptions.Unauthenticated)
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
        if self._session is None:
            raise (exceptions.Unauthenticated)
        requests.put(
            f"https://scratch.mit.edu/site-api/users/bookmarkers/{self.id}/remove/?usernames={self._session._username}",
            headers=headers,
            cookies=self._cookies,
            timeout=10,
        )

    def comments(self, *, limit=None, offset=0):
        """
        Returns the comments posted on the studio (except for replies. To get replies use :meth:`scratchattach.studio.Studio.get_comment_replies`).

        Keyword Arguments:
            page: The page of the comments that should be returned.
            limit: Max. amount of returned comments.

        Returns:
            list<dict>: A list containing the requested comments as dicts.
        """

        url = f"https://api.scratch.mit.edu/studios/{self.id}/comments"

        api_data = api_iterative_simple(
            url,
            limit,
            offset,
            max_req_limit=40,
            add_params=f"&cachebust={random.randint(0,9999)}",
        )
        return api_data

    def get_comment_replies(self, *, comment_id, limit=None, offset=0):
        url = f"https://api.scratch.mit.edu/studios/{self.id}/comments/{comment_id}/replies"

        api_data = api_iterative_simple(
            url,
            limit,
            offset,
            max_req_limit=40,
            add_params=f"&cachebust={random.randint(0,9999)}",
        )
        return api_data

    def get_comment(self, comment_id):
        r = requests.get(
            f"https://api.scratch.mit.edu/studios/{self.id}/comments/{comment_id}",
            timeout=10,
        ).json()
        return r

    def post_comment(self, content, *, parent_id="", commentee_id=""):
        """
        Posts a comment on the studio. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_studio`

        Args:
            content: Content of the comment that should be posted

        Keyword Arguments:
            parent_id: ID of the comment you want to reply to. If you don't want to mention a user, don't put the argument.
            commentee_id: ID of the user that will be mentioned in your comment and will receive a message about your comment. If you don't want to mention a user, don't put the argument.
        """
        if self._session is None:
            raise (exceptions.Unauthenticated)
        data = {
            "commentee_id": commentee_id,
            "content": str(content),
            "parent_id": parent_id,
        }
        headers = self._json_headers
        headers["referer"] = "https://scratch.mit.edu/projects/" + str(self.id) + "/"
        return requests.post(
            f"https://api.scratch.mit.edu/proxy/comments/studio/{self.id}/",
            headers=headers,
            cookies=self._cookies,
            data=json.dumps(data),
            timeout=10,
        ).json()

    def set_thumbnail(self, *, file):
        """
        Sets the studio thumbnail. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_studio`

        Keyword Arguments:
            file: The path to the image file

        Returns:
            str: Scratch cdn link to the set thumbnail
        """
        # "multipart/form-data; boundary=----WebKitFormBoundaryhKZwFjoxAyUTMlSh"
        # multipart/form-data; boundary=----WebKitFormBoundaryqhfwZe4EG6BlJoAK
        if self._session is None:
            raise (exceptions.Unauthenticated)
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

        Keyword Arguments:
            parent_id: ID of the comment you want to reply to
            commentee_id: ID of the user that will be mentioned in your comment and will receive a message about your comment. If you don't want to mention a user, don't put the argument.
        """
        return self.post_comment(
            content, parent_id=parent_id, commentee_id=commentee_id
        )

    def projects(self, limit=None, offset=0):
        """
        Gets the studio projects.

        Keyword arguments:
            limit (int): Max amount of returned projects.
            offset (int): Offset of the first returned project.

        Returns:
            list<scratchattach.project.Project>: A list containing the studio projects as Project objects
        """

        url = f"https://api.scratch.mit.edu/studios/{self.id}/projects"

        api_data = api_iterative_simple(
            url,
            limit,
            offset,
            max_req_limit=40,
        )
        return api_data

    def curators(self, limit=None, offset=0):
        """
        Gets the studio curators.

        Keyword arguments:
            limit (int): Max amount of returned curators.
            offset (int): Offset of the first returned curator.

        Returns:
            list<scratchattach.user.User>: A list containing the studio curators as User objects
        """

        url = f"https://api.scratch.mit.edu/studios/{self.id}/curators"

        raw_curators = api_iterative_simple(
            url,
            limit,
            offset,
            max_req_limit=40,
        )

        curators = []
        for c in raw_curators:
            u = user.User(username=c["username"], session=self._session)
            u._update_from_dict(c)
            curators.append(u)
        return curators

    def invite_curator(self, curator):
        """
        You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_studio`
        """
        if self._session is None:
            raise (exceptions.Unauthenticated)
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
        if self._session is None:
            raise (exceptions.Unauthenticated)
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
        if self._session is None:
            raise (exceptions.Unauthenticated)
        try:
            return requests.put(
                f"https://scratch.mit.edu/site-api/users/curators-in/{self.id}/remove/?usernames={curator}",
                headers=headers,
                cookies=self._cookies,
                timeout=10,
            ).json()
        except Exception:
            raise (exceptions.Unauthorized)

    def leave(self):
        """
        Removes yourself from the studio. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_studio`
        """
        if self._session is None:
            raise (exceptions.Unauthenticated)
        return self.remove_curator(self._session._username)

    def add_project(self, project_id):
        """
        Adds a project to the studio. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_studio`

        Args:
            project_id: Project id of the project that should be added
        """
        if self._session is None:
            raise (exceptions.Unauthenticated)
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
        if self._session is None:
            raise (exceptions.Unauthenticated)
        return requests.delete(
            f"https://api.scratch.mit.edu/studios/{self.id}/project/{project_id}",
            headers=self._headers,
            timeout=10,
        ).json()

    def managers(self, limit=None, offset=0):
        """
        Gets the studio managers.

        Keyword arguments:
            limit (int): Max amount of returned managers
            offset (int): Offset of the first returned manager.

        Returns:
            list<scratchattach.user.User>: A list containing the studio managers as user objects
        """
        url = f"https://api.scratch.mit.edu/studios/{self.id}/managers"

        raw_managers = api_iterative_simple(
            url,
            limit,
            offset,
            max_req_limit=40,
        )

        managers = []
        for c in raw_managers:
            u = user.User(username=c["username"], _session=self._session)
            u._update_from_dict(c)
            managers.append(u)
        return managers

    def host(self):
        """
        Gets the studio host.

        Returns:
            scratchattach.user.User: An object representing the studio host.
        """
        managers = self.managers(limit=1, offset=0)
        if managers:
            return managers[0]
        else:
            return None

    def set_description(self, new):
        """
        You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_studio`
        """
        if self._session is None:
            raise (exceptions.Unauthenticated)
        requests.put(
            f"https://scratch.mit.edu/site-api/galleries/all/{self.id}/",
            headers=headers,
            cookies=self._cookies,
            data=json.dumps({"description": new + "\n"}),
            timeout=10,
        )

    def set_title(self, new):
        """
        You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_studio`
        """
        if self._session is None:
            raise (exceptions.Unauthenticated)
        requests.put(
            f"https://scratch.mit.edu/site-api/galleries/all/{self.id}/",
            headers=headers,
            cookies=self._cookies,
            data=json.dumps({"title": new}),
            timeout=10,
        )

    def open_projects(self):
        """
        Changes the studio settings so everyone (including non-curators) is able to add projects to the studio. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_studio`
        """
        if self._session is None:
            raise (exceptions.Unauthenticated)
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
        if self._session is None:
            raise (exceptions.Unauthenticated)
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
        if self._session is None:
            raise (exceptions.Unauthenticated)
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
        if self._session is None:
            raise (exceptions.Unauthenticated)
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
        if self._session is None:
            raise (exceptions.Unauthenticated)
        requests.post(
            f"https://scratch.mit.edu/site-api/comments/gallery/{self.id}/toggle-comments/",
            headers=headers,
            cookies=self._cookies,
            timeout=10,
        )
        self.comments_allowed = not self.comments_allowed

    def activity(self, *, limit=None, offset=0):
        url = f"https://api.scratch.mit.edu/studios/{self.id}/activity"

        api_data = api_iterative_simple(
            url,
            limit,
            offset,
            max_req_limit=40,
        )
        return api_data

    def accept_invite(self):
        if self._session is None:
            raise (exceptions.Unauthenticated)
        return requests.put(
            f"https://scratch.mit.edu/site-api/users/curators-in/{self.id}/add/?usernames={self._session._username}",
            headers=headers,
            cookies=self._cookies,
            timeout=10,
        ).json()


def get_studio(studio_id):
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
    try:
        studio = Studio(id=int(studio_id))
        if studio.update() == "429":
            raise (
                exceptions.Response429(
                    "Your network is blocked or rate-limited by Scratch.\nIf you're using an online IDE like replit.com, try running the code on your computer."
                )
            )
        return studio
    except KeyError:
        return None
    except Exception as e:
        raise (e)


def search_studios(*, query="", mode="trending", language="en", limit=None, offset=0):
    if not query:
        raise ValueError("The query can't be empty for search")

    url = "https://api.scratch.mit.edu/search/studios"

    api_data = api_iterative_simple(
        url,
        limit,
        offset,
        max_req_limit=40,
        add_params=f"&language={language}&mode={mode}&q={query}",
    )
    return api_data


def explore_studios(*, query="", mode="trending", language="en", limit=None, offset=0):
    url = "https://api.scratch.mit.edu/explore/studios"

    api_data = api_iterative_simple(
        url,
        limit,
        offset,
        max_req_limit=40,
        add_params=f"&language={language}&mode={mode}&q={query}",
    )
    return api_data
