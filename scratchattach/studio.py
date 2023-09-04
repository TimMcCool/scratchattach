#----- Getting studios

import json
import requests
from . import user
from . import exceptions
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
    "x-csrftoken": "a",
    "x-requested-with": "XMLHttpRequest",
    "referer": "https://scratch.mit.edu",
}

class Studio:
    '''
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

    '''

    def __init__(self, **entries):

        self.__dict__.update(entries)

        if "_session" not in self.__dict__.keys():
            self._session = None
        if self._session is None:
            self._headers = headers
            self._cookies = {}
        else:
            self._headers = self._session._headers
            self._cookies = self._session._cookies

        try:
            self._headers.pop("Cookie")
        except Exception: pass
        self._json_headers = self._headers
        self._json_headers["accept"] = "application/json"
        self._json_headers["Content-Type"] = "application/json"

    def update(self):
        """
        Updates the attributes of the Studio object
        """
        studio = requests.get(f"https://api.scratch.mit.edu/studios/{self.id}")
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
        requests.put(
            f"https://scratch.mit.edu/site-api/users/bookmarkers/{self.id}/add/?usernames={self._session._username}",
            headers = headers,
            cookies = self._cookies,
        )

    def unfollow(self):
        """
        You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_studio`
        """
        requests.put(
            f"https://scratch.mit.edu/site-api/users/bookmarkers/{self.id}/remove/?usernames={self._session._username}",
            headers = headers,
            cookies = self._cookies,
        )

    def comments(self, *, limit=40, offset=0):
        """
        Returns the comments posted on the studio (except for replies. To get replies use :meth:`scratchattach.studio.Studio.get_comment_replies`).

        Keyword Arguments:
            page: The page of the comments that should be returned.
            limit: Max. amount of returned comments.

        Returns:
            list<dict>: A list containing the requested comments as dicts.
        """
        comments = []
        while len(comments) < limit:
            r = requests.get(
                f"https://api.scratch.mit.edu/studios/{self.id}/comments/?limit={min(40, limit-len(comments))}&offset={offset}"
            ).json()
            if len(r) != 40:
                comments = comments + r
                break
            offset += 40
            comments = comments + r
        return comments

    def get_comment_replies(self, *, comment_id, limit=40, offset=0):
        comments = []
        while len(comments) < limit:
            r = requests.get(
                f"https://api.scratch.mit.edu/studios/{self.id}/comments/{comment_id}/replies?limit={min(40, limit-len(comments))}&offset={offset}"
            ).json()
            if len(r) != 40:
                comments = comments + r
                break
            offset += 40
            comments = comments + r
        return comments


    def post_comment(self, content, *, parent_id="", commentee_id=""):
        """
        Posts a comment on the studio. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_studio`

        Args:
            content: Content of the comment that should be posted

        Keyword Arguments:
            parent_id: ID of the comment you want to reply to. If you don't want to mention a user, don't put the argument.
            commentee_id: ID of the user that will be mentioned in your comment and will receive a message about your comment. If you don't want to mention a user, don't put the argument.
        """
        if self._headers is None:
            raise(_exceptions.Unauthenticated)
            return
        data = {
            "commentee_id": commentee_id,
            "content": str(content),
            "parent_id": parent_id,
        }
        headers = self._json_headers
        headers["referer"] = "https://scratch.mit.edu/projects/" + str(self.id) + "/"
        return requests.post(
            f"https://api.scratch.mit.edu/proxy/comments/studio/{self.id}/",
            headers = headers,
            cookies = self._cookies,
            data=json.dumps(data),
        ).json()

    def set_thumbnail(self, *, file):
        """
        Sets the studio thumbnail. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_studio`

        Keyword Arguments:
            file: The path to the image file

        Returns:
            str: Scratch cdn link to the set thumbnail
        """
        #"multipart/form-data; boundary=----WebKitFormBoundaryhKZwFjoxAyUTMlSh"
        #multipart/form-data; boundary=----WebKitFormBoundaryqhfwZe4EG6BlJoAK
        if self._headers is None:
            raise(exceptions.Unauthenticated)
            return
        with open(file, "rb") as f:
            thumbnail = f.read()

        filename = file.replace("\\","/")
        if filename.endswith("/"):
            filename = filename[:-1]
        filename = filename.split("/").pop()

        file_type = filename.split(".").pop()

        payload1 = f"------WebKitFormBoundaryhKZwFjoxAyUTMlSh\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{filename}\"\r\nContent-Type: image/{file_type}\r\n\r\n"
        payload1 = payload1.encode("utf-8")
        payload2 = b"\r\n------WebKitFormBoundaryhKZwFjoxAyUTMlSh--\r\n"
        payload = b''.join([payload1, thumbnail, payload2])

        r = requests.post(
            f"https://scratch.mit.edu/site-api/galleries/all/{self.id}/",
            headers = {
                "accept": "*/",
                "content-type": "multipart/form-data; boundary=----WebKitFormBoundaryhKZwFjoxAyUTMlSh",
                "Referer": f"https://scratch.mit.edu/",
                "x-csrftoken": "a",
                "x-requested-with": "XMLHttpRequest"
            },
            data = payload,
            cookies = self._cookies,
        ).json()

        if "errors" in r:
            raise(exceptions.BadRequest(", ".join(r["errors"])))
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
        return self.post_comment(content, parent_id=parent_id, commentee_id=commentee_id)

    def projects(self, limit=40, offset=0):
        """
        Gets the studio projects.

        Keyword arguments:
            limit (int): Max amount of returned projects (can't exceed 40).
            offset (int): Offset of the first returned project.

        Returns:
            list<scratchattach.project.Project>: A list containing the studio projects as Project objects
        """
        return requests.get(f"https://api.scratch.mit.edu/studios/{self.id}/projects/?limit={limit}&offset={offset}").json()

    def curators(self, limit=24, offset=0):
        """
        Gets the studio curators.

        Keyword arguments:
            limit (int): Max amount of returned curators (can't exceed 40).
            offset (int): Offset of the first returned curator.

        Returns:
            list<scratchattach.user.User>: A list containing the studio curators as User objects
        """
        if limit>40:
            limit=40
        raw_curators = requests.get(f"https://api.scratch.mit.edu/studios/{self.id}/curators/?limit={limit}&offset={offset}").json()
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
        try:
            return requests.put(
                f"https://scratch.mit.edu/site-api/users/curators-in/{self.id}/invite_curator/?usernames={curator}",
                headers = headers,
                cookies = self._cookies,
            ).json()
        except Exception:
            raise(_exceptions.Unauthorized)

    def promote_curator(self, curator):
        """
        You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_studio`
        """
        try:
            return requests.put(
                f"https://scratch.mit.edu/site-api/users/curators-in/{self.id}/promote/?usernames={curator}",
                headers = headers,
                cookies = self._cookies
            ).json()
        except Exception:
            raise(_exceptions.Unauthorized)


    def remove_curator(self, curator):
        """
        You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_studio`
        """
        try:
            return requests.put(
                f"https://scratch.mit.edu/site-api/users/curators-in/{self.id}/remove/?usernames={curator}",
                headers = headers,
                cookies = self._cookies
            ).json()
        except Exception:
            raise(_exceptions.Unauthorized)

    def leave(self):
        """
        Removes yourself from the studio. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_studio`
        """
        return self.remove_curator(self._session._username)

    def add_project(self, project_id):
        """
        Adds a project to the studio. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_studio`

        Args:
            project_id: Project id of the project that should be added
        """
        return requests.post(
            f"https://api.scratch.mit.edu/studios/{self.id}/project/{project_id}",
            headers = self._headers
        ).json()

    def remove_project(self, project_id):
        """
        Removes a project from the studio. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_studio`

        Args:
            project_id: Project id of the project that should be removed
        """
        return requests.delete(
            f"https://api.scratch.mit.edu/studios/{self.id}/project/{project_id}",
            headers = self._headers
        ).json()

    def managers(self, limit=24, offset=0):
        """
        Gets the studio managers.

        Keyword arguments:
            limit (int): Max amount of returned managers (can't exceed 40).
            offset (int): Offset of the first returned manager.

        Returns:
            list<scratchattach.user.User>: A list containing the studio managers as user objects
        """
        if limit>40:
            limit=40
        raw_m = requests.get(f"https://api.scratch.mit.edu/studios/{self.id}/managers/?limit={limit}&offset={offset}").json()
        managers = []
        for c in raw_m:
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
        if self.managers != []:
            return managers[0]
        else:
            return None

    def set_description(self, new):
        """
        You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_studio`
        """
        requests.put(
            f"https://scratch.mit.edu/site-api/galleries/all/{self.id}/",
            headers = headers,
            cookies = self._cookies,
            data=json.dumps({"description":new+"\n"})
        )

    def set_title(self, new):
        """
        You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_studio`
        """
        requests.put(
            f"https://scratch.mit.edu/site-api/galleries/all/{self.id}/",
            headers = headers,
            cookies = self._cookies,
            data=json.dumps({"title":new}))

    def open_projects(self):
        """
        Changes the studio settings so everyone (including non-curators) is able to add projects to the studio. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_studio`
        """
        requests.put(
            f"https://scratch.mit.edu/site-api/galleries/{self.id}/mark/open/",
            headers = headers,
            cookies = self._cookies,
        )


    def close_projects(self):
        """
        Changes the studio settings so only curators can add projects to the studio. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_studio`
        """
        requests.put(
            f"https://scratch.mit.edu/site-api/galleries/{self.id}/mark/closed/",
            headers = headers,
            cookies = self._cookies,
        )

    def turn_off_commenting(self):
        """
        You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_studio`
        """
        if self.comments_allowed:
            requests.post(
                f"https://scratch.mit.edu/site-api/comments/gallery/{self.id}/toggle-comments/",
                headers = headers,
                cookies = self._cookies,

            )
            self.comments_allowed = not self.comments_allowed

    def turn_on_commenting(self):
        """
        You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_studio`
        """
        if not self.comments_allowed:
            requests.post(
                f"https://scratch.mit.edu/site-api/comments/gallery/{self.id}/toggle-comments/",
                headers = headers,
                cookies = self._cookies,

            )
            self.comments_allowed = not self.comments_allowed

    def toggle_commenting(self):
        """
        You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_studio`
        """
        requests.post(
            f"https://scratch.mit.edu/site-api/comments/gallery/{self.id}/toggle-comments/",
            headers = headers,
            cookies = self._cookies,
        )
        self.comments_allowed = not self.comments_allowed

    def activity(self, *, limit=20, offset=0):
        if limit>40:
            limit=40
        return requests.get(
            f"https://api.scratch.mit.edu/studios/{self.id}/activity/?limit={limit}&offset={offset}",
            headers = headers
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
            raise(exceptions.Response429("Your network is blocked or rate-limited by Scratch.\nIf you're using an online IDE like replit.com, try running the code on your computer."))
        return studio
    except KeyError:
        return None
    except Exception as e:
        raise(e)

def search_studios(*, query="", mode="trending", language="en", limit=40, offset=0):
    return requests.get(f"https://api.scratch.mit.edu/search/studios?limit={limit}&offset={offset}&language={language}&mode={mode}&q={query}").json()

def explore_studios(*, query="", mode="trending", language="en", limit=40, offset=0):
    return requests.get(f"https://api.scratch.mit.edu/explore/studios?limit={limit}&offset={offset}&language={language}&mode={mode}&q={query}").json()
