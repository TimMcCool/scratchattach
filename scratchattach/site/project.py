"""Project and PartialProject classes"""
from __future__ import annotations

import json
import random
import base64
import time
import warnings
import zipfile
from io import BytesIO
from typing import Callable, Union

from dataclasses import dataclass, field
from typing import Any, Optional
from typing_extensions import deprecated

from scratchattach.site.typed_dicts import ProjectDict
from . import user, comment, studio, session
from scratchattach.utils import exceptions
from scratchattach.utils import commons
from scratchattach.utils.commons import empty_project_json, headers
from ._base import BaseSiteComponent
# from scratchattach.other.project_json_capabilities import ProjectBody
from scratchattach import editor
from scratchattach.utils.requests import requests

CREATE_PROJECT_USES: list[float] = []

@dataclass
class PartialProject(BaseSiteComponent):
    """
    Represents an unshared Scratch project that can't be accessed.
    """
    id: Union[str, int] = field(kw_only=True, default=0)
    "The project id"
    url: str = field(kw_only=True, default="")
    "The project url"
    title: str = field(kw_only=True, default="")
    author_name: str = field(kw_only=True, default="")
    "The username of the author"
    comments_allowed: bool = field(kw_only=True, default=False)
    "whether comments are enabled"
    instructions: str = field(kw_only=True, default="")
    notes: str = field(kw_only=True, default="")
    "The 'Notes and Credits' section"
    created: str = field(kw_only=True, default="")
    "The date of the project creation"
    last_modified: str = field(kw_only=True, default="")
    "The date when the project was modified the last time"
    share_date: str = field(kw_only=True, default="")
    thumbnail_url: str = field(kw_only=True, default="")
    remix_parent: Optional[Union[str, int]] = field(kw_only=True, default="")
    parent_title: Optional[str] = field(kw_only=True, default=None)
    remix_root: Optional[Union[str, int]] = field(kw_only=True, default="")
    loves: int = field(kw_only=True, default=0)
    "The project's love count"
    favorites: int = field(kw_only=True, default=0)
    "The project's favorite count"
    remix_count: int = field(kw_only=True, default=0)
    "The number of remixes"
    views: int = field(kw_only=True, default=0)
    "The view count"
    project_token: Optional[str] = field(kw_only=True, default=None)
    "The project token (required to access the project json)"
    _moderation_status: Optional[str] = field(kw_only=True, default=None)
    _session: Optional[session.Session] = field(kw_only=True, default=None)

    def __str__(self):
        return f"Unshared project with id {self.id}"

    def __post_init__(self) -> None:

        # Info on how the .update method has to fetch the data:
        self.update_function: Callable = requests.get
        self.update_api = f"https://api.scratch.mit.edu/projects/{self.id}"

        # Headers and cookies:
        if self._session is None:
            self._headers = headers
            self._cookies = {}
        else:
            self._headers = self._session.get_headers()
            self._cookies = self._session.get_cookies()

        # Headers for operations that require accept and Content-Type fields:
        self._json_headers = dict(self._headers)
        self._json_headers["accept"] = "application/json"
        self._json_headers["Content-Type"] = "application/json"

    def _update_from_dict(self, data: ProjectDict):
        try:
            self.id = int(data["id"])
        except KeyError:
            pass
        try:
            self.url = f"https://scratch.mit.edu/projects/{self.id}"
        except KeyError:
            pass
        try:
            self.author_name = data["author"]["username"]
        except KeyError:
            pass
        try:
            self.author_name = data["username"]  # type: ignore[typeddict-item]
        except KeyError:
            pass
        try:
            self.comments_allowed = data["comments_allowed"]
        except KeyError:
            pass
        try:
            self.instructions = data["instructions"]
        except KeyError:
            pass
        try:
            self.notes = data["description"]
        except KeyError:
            pass
        try:
            self.created = data["history"]["created"]
        except KeyError:
            pass
        try:
            self.last_modified = data["history"]["modified"]
        except KeyError:
            pass
        try:
            self.share_date = data["history"]["shared"]
        except KeyError:
            pass
        try:
            self.thumbnail_url = data["image"]
        except KeyError:
            pass
        try:
            self.remix_parent = data["remix"]["parent"]
            self.remix_root = data["remix"]["root"]
        except KeyError:
            self.remix_parent = None
            self.remix_root = None
        try:
            self.favorites = data["stats"]["favorites"]
        except KeyError:
            pass
        try:
            self.loves = data["stats"]["loves"]
        except KeyError:
            pass
        try:
            self.remix_count = data["stats"]["remixes"]
        except KeyError:
            pass
        try:
            self.views = data["stats"]["views"]
        except KeyError:
            pass
        try:
            self.title = data["title"]
        except KeyError:
            pass
        try:
            self.project_token = data["project_token"]
        except KeyError:
            self.project_token = None
        if "code" in data:  # Project is unshared -> return false
            return False
        return True

    def __rich__(self):
        from rich.panel import Panel
        from rich.table import Table
        from rich import box
        from rich.markup import escape

        url = f"[link={self.url}]{self.title}[/]"

        ret = Table.grid(expand=True)
        ret.add_column(ratio=1)
        ret.add_column(ratio=3)

        info = Table(box=box.SIMPLE)
        info.add_column(url, overflow="fold")
        info.add_column(f"#{self.id}", overflow="fold")

        info.add_row("By", self.author_name)
        info.add_row("Created", escape(self.created))
        info.add_row("Shared", escape(self.share_date))
        info.add_row("Modified", escape(self.last_modified))
        info.add_row("Comments allowed", escape(str(self.comments_allowed)))
        info.add_row("Loves", str(self.loves))
        info.add_row("Faves", str(self.favorites))
        info.add_row("Remixes", str(self.remix_count))
        info.add_row("Views", str(self.views))

        desc = Table(box=box.SIMPLE)
        desc.add_row("Instructions", escape(self.instructions))
        desc.add_row("Notes & Credits", escape(self.notes))

        ret.add_row(Panel(info, title=url), Panel(desc, title="Description"))

        return ret

    @property
    def embed_url(self):
        """
        Returns:
             the url of the embed of the project
        """
        return f"{self.url}/embed"

    def remixes(self, *, limit=40, offset=0) -> list[Project]:
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

    def raw_json_or_empty(self) -> dict[str, Any]:
        return empty_project_json

    def create_remix(self, *, title=None, project_json=None):  # not working
        """
        Creates a project on the Scratch website.

        Warning:
            Don't spam this method - it WILL get you banned from Scratch.
            To prevent accidental spam, a rate limit (5 projects per minute) is implemented for this function.
        """
        self._assert_auth()

        if title is None:
            if "title" in self.__dict__:
                title = self.title + " remix"
            else:
                title = " remix"
        if project_json is None:
            project_json = self.raw_json_or_empty()

        if len(CREATE_PROJECT_USES) < 5:
            CREATE_PROJECT_USES.insert(0, time.time())
        else:
            if CREATE_PROJECT_USES[-1] < time.time() - 300:
                CREATE_PROJECT_USES.pop()
            else:
                raise exceptions.BadRequest(
                    "Rate limit for remixing Scratch projects exceeded.\nThis rate limit is enforced by scratchattach, not by the Scratch API.\nFor security reasons, it cannot be turned off.\n\nDon't spam-create projects, it WILL get you banned.")
            CREATE_PROJECT_USES.insert(0, time.time())

        params = {
            'is_remix': '1',
            'original_id': self.id,
            'title': title,
        }

        response = requests.post('https://projects.scratch.mit.edu/', params=params, cookies=self._cookies,
                                 headers=self._headers, json=project_json).json()
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

@dataclass
class Project(PartialProject):
    """
    Represents a Scratch project.
    """

    def __repr__(self):
        return f"-P {self.id} ({self.title})"

    def __str__(self):
        return repr(self)

    @property
    def thumbnail(self) -> bytes:
        with requests.no_error_handling():
            return requests.get(self.thumbnail_url).content

    def _assert_permission(self):
        self._assert_auth()
        if self._session.username != self.author_name:
            raise exceptions.Unauthorized(
                "You need to be authenticated as the profile owner to do this.")

    def load_description(self):
        # Overrides the load_description method that exists for unshared projects
        self.update()
    
    # -- Project contents (body/json) -- #
    
    def download(self, *, filename=None, dir="."):
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
                dir += "/"
            self.update()
            response = requests.get(
                f"https://projects.scratch.mit.edu/{self.id}?token={self.project_token}",
                timeout=10,
            )
            filename = filename.removesuffix(".sb3")
            with open(f"{dir}{filename}.sb3", "wb") as f:
                f.write(response.content)
        except Exception as exc:
            raise (
                exceptions.FetchError(
                    "Method only works for projects created with Scratch 3"
                )
            ) from exc
    
    @deprecated("Use raw_json instead")
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

        except Exception as exc:
            raise (
                exceptions.FetchError(
                    "Method only works for projects created with Scratch 3"
                )
            ) from exc

    def body(self) -> editor.Project:
        """
        Method only works for project created with Scratch 3.

        Returns:
            scratchattach.editor.Project: The contents of the project as editor Project object
        """
        raw_json = self.raw_json()
        return editor.Project.from_json(raw_json)

    def raw_json(self):
        """
        Method only works for project created with Scratch 3.

        Returns:
            dict: The raw project JSON as decoded Python dictionary
        """
        try:
            self.update()

        except Exception as e:
            raise (
                exceptions.FetchError(
                    f"You're not authorized for accessing {self}.\nException: {e}"
                )
            )

        with requests.no_error_handling():
            resp = requests.get(
                f"https://projects.scratch.mit.edu/{self.id}?token={self.project_token}",
                timeout=10,
            )

            try:
                return resp.json()
            except json.JSONDecodeError:
                # I am not aware of any cases where this will not be a zip file
                # in the future, cache a projectbody object here and just return the json
                # that is fetched from there to not waste existing asset data from this zip file

                with zipfile.ZipFile(BytesIO(resp.content)) as zipf:
                    return json.load(zipf.open("project.json"))

    def raw_json_or_empty(self):
        return self.raw_json()

    def creator_agent(self):
        """
        Method only works for project created with Scratch 3.

        Returns:
            str: The user agent of the browser that this project was saved with.
        """
        return self.raw_json()["meta"]["agent"]

    def set_body(self, project_body: editor.Project):
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

    def upload_json_from(self, project_id: int | str):
        """
        Uploads the project json from the project with the given id to the project represented by this Project object
        """
        self._assert_auth()
        other_project = self._session.connect_project(project_id)  # type: ignore
        self.set_json(other_project.raw_json())

    # -- other -- #
    
    def author(self) -> user.User:
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
            f"https://api.scratch.mit.edu/users/{self.author_name}/projects/{self.id}/studios", limit=limit,
            offset=offset, add_params=f"&cachebust={random.randint(0, 9999)}")
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
            f"https://api.scratch.mit.edu/users/{self.author_name}/projects/{self.id}/comments/", limit=limit,
            offset=offset, add_params=f"&cachebust={random.randint(0, 9999)}")
        for i in response:
            i["source"] = "project"
            i["source_id"] = self.id
        return commons.parse_object_list(response, comment.Comment, self._session)

    def comment_replies(self, *, comment_id, limit=40, offset=0):
        response = commons.api_iterative(
            f"https://api.scratch.mit.edu/users/{self.author_name}/projects/{self.id}/comments/{comment_id}/replies/",
            limit=limit, offset=offset, add_params=f"&cachebust={random.randint(0, 9999)}")
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
        # https://api.scratch.mit.edu/users/TimMcCool/projects/404369790/comments/439984518
        data = requests.get(
            f"https://api.scratch.mit.edu/users/{self.author_name}/projects/{self.id}/comments/{comment_id}",
            headers=self._headers,
            cookies=self._cookies
        ).json()

        if data is None or data.get("code") == "NotFound":
            raise exceptions.CommentNotFound(
                f"Cannot find comment #{comment_id} on -P {self.id} by -U {self.author_name}")

        _comment = comment.Comment(id=data["id"], _session=self._session, source=comment.CommentSource.PROJECT,
                                   source_id=self.id)
        _comment._update_from_dict(data)
        return _comment

    def love(self):
        """
        Posts a love on the project. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_project`
        """
        self._assert_auth()
        r = requests.post(
            f"https://api.scratch.mit.edu/proxy/projects/{self.id}/loves/user/{self._session.username}",
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
            f"https://api.scratch.mit.edu/proxy/projects/{self.id}/loves/user/{self._session.username}",
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
            f"https://api.scratch.mit.edu/proxy/projects/{self.id}/favorites/user/{self._session.username}",
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
            f"https://api.scratch.mit.edu/proxy/projects/{self.id}/favorites/user/{self._session.username}",
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
            For example, you can also share / unshare the project by setting the "shared" field.
            According to the Scratch team, this API is deprecated. As of 2024 it's still fully functional though.
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
        )

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
        r = json.loads(
            requests.post(
                f"https://api.scratch.mit.edu/proxy/comments/project/{self.id}/",
                headers=(self._json_headers | {"referer": "https://scratch.mit.edu/projects/" + str(self.id) + "/"}),
                cookies=self._cookies,
                data=json.dumps(data),
            ).text
        )
        if "id" not in r:
            raise exceptions.CommentPostFailure(r)
        _comment = comment.Comment(id=r["id"], _session=self._session, source=comment.CommentSource.PROJECT,
                                   source_id=self.id)
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

    @deprecated("Deprecated because ScratchDB is down indefinitely.")
    def ranks(self):
        """
        Gets information about the project's ranks. Fetched from ScratchDB.

        Warning:
            This method is deprecated because ScratchDB is down indefinitely.

        Returns:
            dict: A dict containing the project's ranks. If the ranks aren't available, all values will be -1.
        """
        return requests.get(
            f"https://scratchdb.lefty.one/v3/project/info/{self.id}"
        ).json()["statistics"]["ranks"]

    def moderation_status(self, *, reload: bool = False):
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
        if self._moderation_status and not reload:
            return self._moderation_status

        try:
            return requests.get(
                f"https://jeffalo.net/api/nfe/?project={self.id}"
            ).json()["status"]
        except Exception as exc:
            raise exceptions.FetchError from exc

    def visibility(self):
        """
        Returns info about the project's visibility. Requires authentication.
        """
        self._assert_auth()
        return requests.get(f"https://api.scratch.mit.edu/users/{self._session.username}/projects/{self.id}/visibility",
                            headers=self._headers, cookies=self._cookies).json()


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
    warnings.warn(
        "For methods that require authentication, use session.connect_project instead of get_project.\n"
        "If you want to remove this warning, "
        "use `warnings.filterwarnings('ignore', category=scratchattach.ProjectAuthenticationWarning)`.\n"
        "To ignore all warnings of the type GetAuthenticationWarning, which includes this warning, use "
        "`warnings.filterwarnings('ignore', category=scratchattach.GetAuthenticationWarning)`.",
        exceptions.ProjectAuthenticationWarning
    )
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
        "https://api.scratch.mit.edu/search/projects", limit=limit, offset=offset,
        add_params=f"&language={language}&mode={mode}&q={query}")
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
        "https://api.scratch.mit.edu/explore/projects", limit=limit, offset=offset,
        add_params=f"&language={language}&mode={mode}&q={query}")
    return commons.parse_object_list(response, Project)
