"""Project and PartialProject classes"""
from __future__ import annotations

import json
import random
import base64
import time
from . import user, comment, studio
from ..utils import exceptions
from ..utils import commons
from ..utils.commons import empty_project_json, headers
from ._base import BaseSiteComponent
from ..other.project_json_capabilities import ProjectBody
from ..utils.requests import Requests as requests

CREATE_PROJECT_USES = []

class PartialProject(BaseSiteComponent):
    """
    Represents an unshared Scratch project that can't be accessed.
    """

    def __str__(self):
        return f"Unshared project with id {self.id}"

    def __init__(self, **entries):

        # Info on how the .update method has to fetch the data:
        self.update_function = requests.get
        self.update_API = f"https://api.scratch.mit.edu/projects/{entries['id']}"

        # Set attributes every Project object needs to have:
        self._session = None
        self.project_token = None
        self.id = 0
        self.instructions = None
        self.parent_title = None

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

    def _update_from_dict(self, data):
        try:
            self.id = int(data["id"])
        except KeyError:
            pass
        try: self.url = "https://scratch.mit.edu/projects/" + str(self.id)
        except Exception: pass
        try: self.author_name = data["author"]["username"]
        except Exception: pass
        try: self.author_name = data["username"]
        except Exception: pass
        try: self.comments_allowed = data["comments_allowed"]
        except Exception: pass
        try: self.instructions = data["instructions"]
        except Exception: pass
        try: self.notes = data["description"]
        except Exception: pass
        try: self.created = data["history"]["created"]
        except Exception: pass
        try: self.last_modified = data["history"]["modified"]
        except Exception: pass
        try: self.share_date = data["history"]["shared"]
        except Exception: pass
        try: self.thumbnail_url = data["image"]
        except Exception: pass
        try:
            self.remix_parent = data["remix"]["parent"]
            self.remix_root = data["remix"]["root"]
        except Exception:
            self.remix_parent = None
            self.remix_root = None
        try: self.favorites = data["stats"]["favorites"]
        except Exception: pass
        try: self.loves = data["stats"]["loves"]
        except Exception: pass
        try: self.remix_count = data["stats"]["remixes"]
        except Exception: pass
        try: self.views = data["stats"]["views"]
        except Exception: pass
        try: self.title = data["title"]
        except Exception: pass
        try:
            self.project_token = data["project_token"]
        except Exception:
            self.project_token = None
        if "code" in data: # Project is unshared -> return false
            return False
        return True

    @property
    def embed_url(self):
        """
        Returns:
             the url of the embed of the project
        """
        return f"{self.url}/embed"

    def remixes(self, *, limit=40, offset=0):
        """
        Returns:
            list<scratchattach.project.Project>: A list containing the remixes of the project, each project is represented by a Project object.
        """
        response = commons.api_iterative(
            f"https://api.scratch.mit.edu/projects/{self.id}/remixes", limit=limit, offset=offset)
        return commons.parse_object_list(response, Project, self._session)

    def is_shared(self):
        """
        Returns:
            boolean: Returns whether the project is currently shared
        """
        p = get_project(self.id)
        return isinstance(p, Project)
    
    def create_remix(self, *, title=None, project_json=None): # not working
        """
        Creates a project on the Scratch website.

        Warning:
            Don't spam this method - it WILL get you banned from Scratch.
            To prevent accidental spam, a rate limit (5 projects per minute) is implemented for this function.
        """
        self._assert_auth()

        global CREATE_PROJECT_USES

        if title is None:
            if "title" in self.__dict__:
                title = self.title+" remix"
            else:
                title = " remix"
        if project_json is None:
            if "title" in self.__dict__:
                project_json = self.get_raw_json()
            else:
                project_json = empty_project_json

        if len(CREATE_PROJECT_USES) < 5:
            CREATE_PROJECT_USES.insert(0, time.time())
        else:
            if CREATE_PROJECT_USES[-1] < time.time() - 300:
                CREATE_PROJECT_USES.pop()
            else:
                raise exceptions.BadRequest("Rate limit for remixing Scratch projects exceeded.\nThis rate limit is enforced by scratchattach, not by the Scratch API.\nFor security reasons, it cannot be turned off.\n\nDon't spam-create projects, it WILL get you banned.")
                return
            CREATE_PROJECT_USES.insert(0, time.time())

        params = {
            'is_remix': '1',
            'original_id': self.id,
            'title': title,
        }

        response = requests.post('https://projects.scratch.mit.edu/', params=params, cookies=self._cookies, headers=self._headers, json=project_json).json()
        _project = self._session.connect_project(response["content-name"])
        _project.parent_title = base64.b64decode(response['content-title']).decode('utf-8').split(' remix')[0]
        return _project
    
    def load_description(self):
        """
        Gets the instructions of the unshared project. Requires authentication.
        
        Warning:
            It's unclear if Scratch allows using this method. This method will create a remix of the unshared project using your account.
        """
        self._assert_auth()
        new_project = self.create_remix(project_json=empty_project_json)
        self.instructions = new_project.instructions
        self.title = new_project.parent_title


class Project(PartialProject):
    """
    Represents a Scratch project.

    Attributes:

    :.id: The project id

    :.url: The project url

    :.title:

    :.author_name: The username of the author

    :.comments_allowed: boolean that is True if comments are enabled

    :.instructions:

    :.notes: The 'Notes and Credits' section

    :.created: The date of the project creation

    :.last_modified: The date when the project was modified the last time

    :.share_date:

    :.thumbnail_url:

    :.remix_parent:

    :.remix_root:

    :.loves: The project's love count

    :.favorites: The project's favorite count

    :.remix_count: The number of remixes

    :.views: The view count

    :.project_token: The project token (required to access the project json)

    :.update(): Updates the attributes
    """

    def __str__(self):
        return str(self.title)

    def _assert_permission(self):
        self._assert_auth()
        if self._session._username != self.author_name:
            raise exceptions.Unauthorized(
                "You need to be authenticated as the profile owner to do this.")

    def load_description(self):
        # Overrides the load_description method that exists for unshared projects
        self.update()

    def download(self, *, filename=None, dir=""):
        """
        Downloads the project json to the given directory.

        Args:
            filename (str): The name that will be given to the downloaded file.
            dir (str): The path of the directory the file will be saved in.
        """
        try:
            if filename is None:
                filename = str(self.id)
            if not (dir.endswith("/") or dir.endswith("\\")):
                dir = dir+"/"
            self.update()
            response = requests.get(
                f"https://projects.scratch.mit.edu/{self.id}?token={self.project_token}",
                timeout=10,
            )
            filename = filename.replace(".sb3", "")
            open(f"{dir}{filename}.sb3", "wb").write(response.content)
        except Exception:
            raise (
                exceptions.FetchError(
                    "Method only works for projects created with Scratch 3"
                )
            )

    def get_json(self) -> str:
        """
        Downloads the project json and returns it as a string
        """
        try:
            self.update()
            response = requests.get(
                f"https://projects.scratch.mit.edu/{self.id}?token={self.project_token}",
                timeout=10,
            )
            return response.text

        except Exception:
            raise (
                exceptions.FetchError(
                    "Method only works for projects created with Scratch 3"
                )
            )

    def body(self):
        """
        Method only works for project created with Scratch 3.

        Returns:
            scratchattach.ProjectBody: The contents of the project as ProjectBody object
        """
        raw_json = self.raw_json()
        pb = ProjectBody()
        pb.from_json(raw_json)
        return pb

    def raw_json(self):
        """
        Method only works for project created with Scratch 3.

        Returns:
            dict: The raw project JSON as decoded Python dictionary
        """
        try:
            self.update()
            return requests.get(
                f"https://projects.scratch.mit.edu/{self.id}?token={self.project_token}",
                timeout=10,
            ).json()
        except Exception:
            raise (
                exceptions.FetchError(
                    "Either the project was created with an old Scratch version, or you're not authorized for accessing it"
                )
            )
    
    def creator_agent(self):
        """
        Method only works for project created with Scratch 3.

        Returns:
            str: The user agent of the browser that this project was saved with.
        """
        return self.raw_json()["meta"]["agent"]

    def author(self):
        """
        Returns:
            scratchattach.user.User: An object representing the Scratch user who created this project.
        """
        return self._make_linked_object("username", self.author_name, user.User, exceptions.UserNotFound)

    def studios(self, *, limit=40, offset=0):
        """
        Returns:
            list<scratchattach.studio.Studio>: A list containing the studios this project is in, each studio is represented by a Studio object.
        """
        response = commons.api_iterative(
            f"https://api.scratch.mit.edu/users/{self.author_name}/projects/{self.id}/studios", limit=limit, offset=offset, add_params=f"&cachebust={random.randint(0,9999)}")
        return commons.parse_object_list(response, studio.Studio, self._session)

    def comments(self, *, limit=40, offset=0) -> list['comment.Comment']:
        """
        Returns the comments posted on the project (except for replies. To get replies use :meth:`scratchattach.project.Project.comment_replies`).

        Keyword Arguments:
            page: The page of the comments that should be returned.
            limit: Max. amount of returned comments.

        Returns:
            list<scratchattach.comment.Comment>: A list containing the requested comments as Comment objects.
        """

        response = commons.api_iterative(
            f"https://api.scratch.mit.edu/users/{self.author_name}/projects/{self.id}/comments/", limit=limit, offset=offset, add_params=f"&cachebust={random.randint(0,9999)}")
        for i in response:
            i["source"] = "project"
            i["source_id"] = self.id
        return commons.parse_object_list(response, comment.Comment, self._session)

    def comment_replies(self, *, comment_id, limit=40, offset=0):
        response = commons.api_iterative(
            f"https://api.scratch.mit.edu/users/{self.author_name}/projects/{self.id}/comments/{comment_id}/replies/", limit=limit, offset=offset, add_params=f"&cachebust={random.randint(0,9999)}")
        for x in response:
            x["parent_id"] = comment_id
            x["source"] = "project"
            x["source_id"] = self.id
        return commons.parse_object_list(response, comment.Comment, self._session)

    def comment_by_id(self, comment_id):
        """
        Returns:
            scratchattach.comments.Comment: A Comment object representing the requested comment.
        """
        r = requests.get(
            f"https://api.scratch.mit.edu/users/{self.author_name}/projects/{self.id}/comments/{comment_id}",
            headers=self._headers,
            cookies=self._cookies
        ).json()
        if r is None:
            raise exceptions.CommentNotFound()
        _comment = comment.Comment(id=r["id"], _session=self._session, source="project", source_id=self.id)
        _comment._update_from_dict(r)
        return _comment
    
    def love(self):
        """
        Posts a love on the project. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_project`
        """
        self._assert_auth()
        r = requests.post(
            f"https://api.scratch.mit.edu/proxy/projects/{self.id}/loves/user/{self._session._username}",
            headers=self._headers,
            cookies=self._cookies,
        ).json()
        if "userLove" in r:
            if r["userLove"] is False:
                self.love()
        else:
            raise exceptions.APIError(str(r))

    def unlove(self):
        """
        Removes the love from this project. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_project`
        """
        self._assert_auth()
        r = requests.delete(
            f"https://api.scratch.mit.edu/proxy/projects/{self.id}/loves/user/{self._session._username}",
            headers=self._headers,
            cookies=self._cookies,
        ).json()
        if "userLove" in r:
            if r["userLove"] is True:
                self.unlove()
        else:
            raise exceptions.APIError(str(r))

    def favorite(self):
        """
        Posts a favorite on the project. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_project`
        """
        self._assert_auth()
        r = requests.post(
            f"https://api.scratch.mit.edu/proxy/projects/{self.id}/favorites/user/{self._session._username}",
            headers=self._headers,
            cookies=self._cookies,
        ).json()
        if "userFavorite" in r:
            if r["userFavorite"] is False:
                self.favorite()
        else:
            raise exceptions.APIError(str(r))

    def unfavorite(self):
        """
        Removes the favorite from this project. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_project`
        """
        self._assert_auth()
        r = requests.delete(
            f"https://api.scratch.mit.edu/proxy/projects/{self.id}/favorites/user/{self._session._username}",
            headers=self._headers,
            cookies=self._cookies,
        ).json()
        if "userFavorite" in r:
            if r["userFavorite"] is True:
                self.unfavorite()
        else:
            raise exceptions.APIError(str(r))

    def post_view(self):
        """
        Increases the project's view counter by 1. Doesn't require a login.
        """
        requests.post(
            f"https://api.scratch.mit.edu/users/{self.author_name}/projects/{self.id}/views/",
            headers=headers,
        )

    def set_fields(self, fields_dict, *, use_site_api=False):
        """
        Sets fields. By default, ueses the api.scratch.mit.edu/projects/xxx/ PUT API.

        Keyword Arguments:
        use_site_api (bool):
            When enabled, the fields are set using the scratch.mit.edu/site-api API.
            This function allows setting more fields than Project.set_fields.
            For example you can also share / unshare the project by setting the "shared" field.
            According to the Scratch team, this API is deprecated. As of 2024 it's still fully functional tho.
        """
        self._assert_permission()
        if use_site_api:
            r = requests.put(
                f"https://scratch.mit.edu/site-api/projects/all/{self.id}",
                headers=self._headers,
                cookies=self._cookies,
                json=fields_dict,
            ).json()
        else:
            r = requests.put(
                f"https://api.scratch.mit.edu/projects/{self.id}",
                headers=self._headers,
                cookies=self._cookies,
                json=fields_dict,
            ).json()
        return self._update_from_dict(r)
    
    def turn_off_commenting(self):
        """
        Disables commenting on the project. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_project`
        """
        data = {"comments_allowed": False}
        self.set_fields(data)

    def turn_on_commenting(self):
        """
        Enables commenting on the project. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_project`
        """
        data = {"comments_allowed": True}
        self.set_fields(data)

    def toggle_commenting(self):
        """
        Switches commenting on / off on the project (If comments are on, they will be turned off, else they will be turned on). You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_project`
        """
        data = {"comments_allowed": not self.comments_allowed}
        self.set_fields(data)

    def share(self):
        """
        Shares the project. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_project`
        """
        self._assert_permission()
        requests.put(
            f"https://api.scratch.mit.edu/proxy/projects/{self.id}/share/",
            headers=self._json_headers,
            cookies=self._cookies,
        )

    def unshare(self):
        """
        Unshares the project. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_project`
        """
        self._assert_permission()
        requests.put(
            f"https://api.scratch.mit.edu/proxy/projects/{self.id}/unshare/",
            headers=self._json_headers,
            cookies=self._cookies,
        )

    ''' doesn't work. the API's response is valid (no errors), but the fields don't change
    def move_to_trash(self):
        """
        Moves the project to trash folder. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_project`
        """
        self.set_fields({"id":int(self.id), "visibility": "trshbyusr", "isPublished" : False}, use_site_api=True)'''

    def set_thumbnail(self, *, file):
        """
        You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_project`
        """
        self._assert_permission()
        with open(file, "rb") as f:
            thumbnail = f.read()
        requests.post(
            f"https://scratch.mit.edu/internalapi/project/thumbnail/{self.id}/set/",
            data=thumbnail,
            headers=self._headers,
            cookies=self._cookies,
        )

    def delete_comment(self, *, comment_id):
        """
        Deletes a comment by its ID. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_project`

        Args:
            comment_id: The id of the comment that should be deleted
        """
        self._assert_permission()
        return requests.delete(
            f"https://api.scratch.mit.edu/proxy/comments/project/{self.id}/comment/{comment_id}/",
            headers=self._headers,
            cookies=self._cookies,
        ).headers

    def report_comment(self, *, comment_id):
        """
        Reports a comment by its ID to the Scratch team. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_project`

        Args:
            comment_id: The id of the comment that should be reported
        """
        self._assert_auth()
        return requests.delete(
            f"https://api.scratch.mit.edu/proxy/comments/project/{self.id}/comment/{comment_id}/report",
            headers=self._headers,
            cookies=self._cookies,
        )

    def post_comment(self, content, *, parent_id="", commentee_id=""):
        """
        Posts a comment on the project. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_project`

        Args:
            content: Content of the comment that should be posted

        Keyword Arguments:
            parent_id: ID of the comment you want to reply to. If you don't want to mention a user, don't put the argument.
            commentee_id: ID of the user that will be mentioned in your comment and will receive a message about your comment. If you don't want to mention a user, don't put the argument.
        
        Returns:
            scratchattach.comments.Comment: Comment object representing the posted comment.
        """
        self._assert_auth()
        data = {
            "commentee_id": commentee_id,
            "content": str(content),
            "parent_id": parent_id,
        }
        headers = dict(self._json_headers)
        headers["referer"] = "https://scratch.mit.edu/projects/" + str(self.id) + "/"
        r = json.loads(
            requests.post(
                f"https://api.scratch.mit.edu/proxy/comments/project/{self.id}/",
                headers=headers,
                cookies=self._cookies,
                data=json.dumps(data),
            ).text
        )
        if "id" not in r:
            raise exceptions.CommentPostFailure(r)
        _comment = comment.Comment(id=r["id"], _session=self._session, source="project", source_id=self.id)
        _comment._update_from_dict(r)
        return _comment

    def reply_comment(self, content, *, parent_id, commentee_id=""):
        """
        Posts a reply to a comment on the project. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_project`

        Args:
            content: Content of the comment that should be posted

        Warning:
            Only replies to top-level comments are shown on the Scratch website. Replies to replies are actually replies to the corresponding top-level comment in the API.
            
            Therefore, parent_id should be the comment id of a top level comment.
            
        Keyword Arguments:
            parent_id: ID of the comment you want to reply to
            commentee_id: ID of the user you are replying to
        """
        return self.post_comment(
            content, parent_id=parent_id, commentee_id=commentee_id
        )
    
    def set_body(self, project_body:ProjectBody):
        """
        Sets the project's contents You can use this to upload projects to the Scratch website.
        Returns a dict with Scratch's raw JSON API response.

        Args:
            project_body (scratchattach.ProjectBody): A ProjectBody object containing the contents of the project
        """
        self._assert_permission()
        
        return self.set_json(project_body.to_json())


    def set_json(self, json_data):
        """
        Sets the project json. You can use this to upload projects to the Scratch website.
        Returns a dict with Scratch's raw JSON API response.

        Args:
            json_data (dict or JSON): The new project JSON as encoded JSON object or as dict
        """

        self._assert_permission()

        if not isinstance(json_data, dict):
            json_data = json.loads(json_data)

        return requests.put(
            f"https://projects.scratch.mit.edu/{self.id}",
            headers=self._headers,
            cookies=self._cookies,
            json=json_data,
        ).json()

    def upload_json_from(self, project_id):
        """
        Uploads the project json from the project with the given id to the project represented by this Project object
        """
        self._assert_auth()
        other_project = self._session.connect_project(project_id)
        self.set_json(other_project.get_raw_json())

    def set_title(self, text):
        """
        Changes the projects title. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_project`
        """
        self.set_fields({"title": text})
    

    def set_instructions(self, text):
        """
        Changes the projects instructions. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_project`
        """
        self.set_fields({"instructions": text})

    def set_notes(self, text):
        """
        Changes the projects notes and credits. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_project`
        """
        self.set_fields({"description": text})


    def ranks(self):
        """
        Gets information about the project's ranks. Fetched from ScratchDB.

        Warning:
            This method is deprecated because ScratchDB is down indefinitely.

        Returns:
            dict: A dict containing the project's ranks. If the ranks aren't available, all values will be -1.
        """
        print("Warning: Project.ranks method is deprecated because ScratchDB is down indefinitely.")
        return requests.get(
            f"https://scratchdb.lefty.one/v3/project/info/{self.id}"
        ).json()["statistics"]["ranks"]

    def moderation_status(self):
        """
        Gets information about the project's moderation status. Fetched from jeffalo's API.

        Returns:
            str: The moderation status of the project.

        These moderation statuses exist:

        safe: The project was reviewed by the Scratch team and was considered safe for everyone.

        notsafe: The project was reviewed by the Scratch team and was considered not safe for everyone (nfe). It can't appear in search results, on the explore page and on the front page.

        notreviewed: The project hasn't been reviewed yet.

        no_remixes: Unable to fetch the project's moderation status.
        """
        try:
            return requests.get(
                f"https://jeffalo.net/api/nfe/?project={self.id}"
            ).json()["status"]
        except Exception:
            raise (exceptions.FetchError)

    def visibility(self):
        """
        Returns info about the project's visibility. Requires authentication.
        """
        self._assert_auth()
        return requests.get(f"https://api.scratch.mit.edu/users/{self._session.username}/projects/{self.id}/visibility", headers=self._headers, cookies=self._cookies).json()

# ------ #


def get_project(project_id) -> Project:
    """
    Gets a project without logging in.

    Args:
        project_id (int): Project id of the requested project

    Returns:
        scratchattach.project.Project: An object representing the requested project.

    Warning:
        Any methods that require authentication (like project.love) will not work on the returned object.

        If you want to use these methods, get the project with :meth:`scratchattach.session.Session.connect_project` instead.
    """
    print("Warning: For methods that require authentication, use session.connect_project instead of get_project")
    return commons._get_object("id", project_id, Project, exceptions.ProjectNotFound)

def search_projects(*, query="", mode="trending", language="en", limit=40, offset=0):
    '''
    Uses the Scratch search to search projects.

    Keyword arguments:
        query (str): The query that will be searched.
        mode (str): Has to be one of these values: "trending", "popular" or "recent". Defaults to "trending".
        language (str): A language abbreviation, defaults to "en". (Depending on the language used on the Scratch website, Scratch displays you different results.)
        limit (int): Max. amount of returned projects.
        offset (int): Offset of the first returned project.

    Returns:
        list<scratchattach.project.Project>: List that contains the search results.
    '''
    if not query:
        raise ValueError("The query can't be empty for search")
    response = commons.api_iterative(
        f"https://api.scratch.mit.edu/search/projects", limit=limit, offset=offset, add_params=f"&language={language}&mode={mode}&q={query}")
    return commons.parse_object_list(response, Project)

def explore_projects(*, query="*", mode="trending", language="en", limit=40, offset=0):
    '''
    Gets projects from the explore page.

    Keyword arguments:
        query (str): Specifies the tag of the explore page. To get the projects from the "All" tag, set this argument to "*".
        mode (str): Has to be one of these values: "trending", "popular" or "recent". Defaults to "trending".
        language (str): A language abbreviation, defaults to "en". (Depending on the language used on the Scratch website, Scratch displays you different explore pages.)
        limit (int): Max. amount of returned projects.
        offset (int): Offset of the first returned project.

    Returns:
        list<scratchattach.project.Project>: List that contains the explore page projects.
    '''
    if not query:
        raise ValueError("The query can't be empty for search")
    response = commons.api_iterative(
        f"https://api.scratch.mit.edu/explore/projects", limit=limit, offset=offset, add_params=f"&language={language}&mode={mode}&q={query}")
    return commons.parse_object_list(response, Project)