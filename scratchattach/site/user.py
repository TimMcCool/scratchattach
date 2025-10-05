"""User class"""
from __future__ import annotations

import json
import random
import re
import string
import warnings
from typing import Union, cast, Optional, TypedDict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from typing_extensions import deprecated
from bs4 import BeautifulSoup, Tag

from ._base import BaseSiteComponent
from scratchattach.eventhandlers import message_events

from scratchattach.utils import commons
from scratchattach.utils import exceptions
from scratchattach.utils.commons import headers
from scratchattach.utils.requests import requests

from . import project
from . import studio
from . import forum
from . import comment
from . import activity
from . import classroom
from . import typed_dicts
from . import session

class Rank(Enum):
    """
    Possible ranks in scratch
    """
    NEW_SCRATCHER = 0
    SCRATCHER = 1
    SCRATCH_TEAM = 2

class _OcularStatusMeta(TypedDict):
    updated: str
    updatedBy: str

class _OcularStatus(TypedDict):
    _id: str
    name: str
    status: str
    color: str
    meta: _OcularStatusMeta

class Verificator:

    def __init__(self, user: User, project_id: int):
        self.project = user._make_linked_object("id", project_id, project.Project, exceptions.ProjectNotFound)
        self.projecturl = self.project.url
        self.code = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        self.username = user.username

    def check(self) -> bool:
        return bool(list(filter(lambda x : x.author_name == self.username and (x.content == self.code or x.content.startswith(self.code) or x.content.endswith(self.code)), self.project.comments())))

@dataclass
class User(BaseSiteComponent[typed_dicts.UserDict]):

    '''
    Represents a Scratch user.

    Attributes:

    :.join_date:

    :.about_me:

    :.wiwo: Returns the user's 'What I'm working on' section

    :.country: Returns the country from the user profile

    :.icon_url: Returns the link to the user's pfp (90x90)

    :.id: Returns the id of the user

    :.scratchteam: Retuns True if the user is in the Scratch team

    :.update(): Updates the attributes
    '''
    username: str = field(kw_only=True, default="")
    join_date: str = field(kw_only=True, default="")
    about_me: str = field(kw_only=True, default="")
    wiwo: str = field(kw_only=True, default="")
    country: str = field(kw_only=True, default="")
    icon_url: str = field(kw_only=True, default="")
    id: int = field(kw_only=True, default=0)
    scratchteam: bool = field(kw_only=True, repr=False, default=False)
    _classroom: tuple[bool, Optional[classroom.Classroom]] = field(init=False, default=(False, None))
    _headers: dict[str, str] = field(init=False, default_factory=headers.copy)
    _cookies: dict[str, str] = field(init=False, default_factory=dict)
    _json_headers: dict[str, str] = field(init=False, default_factory=dict)
    _session: Optional[session.Session] = field(kw_only=True, default=None)

    def __str__(self):
        return f"-U {self.username}"

    @property
    def status(self) -> str:
        return self.wiwo

    @property
    def bio(self) -> str:
        return self.about_me

    @property
    def icon(self) -> bytes:
        with requests.no_error_handling():
            return requests.get(self.icon_url).content

    @property
    def name(self) -> str:
        return self.username

    def __post_init__(self):

        # Info on how the .update method has to fetch the data:
        self.update_function = requests.get
        self.update_api = f"https://api.scratch.mit.edu/users/{self.username}"

        # cache value for classroom getter method (using @property)
        # first value is whether the cache has actually been set (because it can be None), second is the value itself
        # self._classroom

        # Headers and cookies:
        if self._session is not None:
            self._headers = self._session.get_headers()
            self._cookies = self._session.get_cookies()

        # Headers for operations that require accept and Content-Type fields:
        self._json_headers = dict(self._headers)
        self._json_headers["accept"] = "application/json"
        self._json_headers["Content-Type"] = "application/json"

    def _update_from_dict(self, data: Union[dict, typed_dicts.UserDict]):
        data = cast(typed_dicts.UserDict, data)
        self.id = data["id"]
        self.username = data["username"]
        self.scratchteam = data["scratchteam"]
        self.join_date = data["history"]["joined"]
        self.about_me = data["profile"]["bio"]
        self.wiwo = data["profile"]["status"]
        self.country = data["profile"]["country"]
        self.icon_url = data["profile"]["images"]["90x90"]
        return True

    def _assert_permission(self):
        self._assert_auth()
        if self._session.username != self.username:
            raise exceptions.Unauthorized(
                "You need to be authenticated as the profile owner to do this.")

    @property
    def url(self):
        return f"https://scratch.mit.edu/users/{self.username}"

    def __rich__(self):
        from rich.panel import Panel
        from rich.table import Table
        from rich import box
        from rich.markup import escape

        featured_data = self.featured_data() or {}
        ocular_data = self.ocular_status()
        ocular = 'No ocular status'

        if status := ocular_data.get("status"):
            color_str = ''
            color_data = ocular_data.get("color")
            if color_data is not None:
                color_str = f"[{color_data}] ⬤ [/]"

            ocular = f"[i]{escape(status)}[/]{color_str}"

        _classroom = self.classroom
        url = f"[link={self.url}]{escape(self.username)}[/]"

        info = Table(box=box.SIMPLE)
        info.add_column(url, overflow="fold")
        info.add_column(f"#{self.id}", overflow="fold")

        info.add_row("Joined", escape(self.join_date))
        info.add_row("Country", escape(self.country))
        info.add_row("Messages", str(self.message_count()))
        info.add_row("Class", str(_classroom.title if _classroom is not None else 'None'))

        desc = Table("Profile", ocular, box=box.SIMPLE)
        desc.add_row("About me", escape(self.about_me))
        desc.add_row("Wiwo", escape(self.wiwo))
        desc.add_row(escape(featured_data.get("label", "Featured Project")),
                     escape(str(self.connect_featured_project())))

        ret = Table.grid(expand=True)

        ret.add_column(ratio=1)
        ret.add_column(ratio=3)
        ret.add_row(Panel(info, title=url), Panel(desc, title="Description"))

        return ret

    def connect_featured_project(self) -> Optional[project.Project]:
        data = self.featured_data() or {}
        if pid := data.get("id"):
            return self._session.connect_project(int(pid))
        if projs := self.projects(limit=1):
            return projs[0]
        return None

    @property
    def classroom(self) -> classroom.Classroom | None:
        """
        Get a user's associated classroom, and return it as a `scratchattach.classroom.Classroom` object.
        If there is no associated classroom, returns `None`
        """
        if not self._classroom[0]:
            with requests.no_error_handling():
                resp = requests.get(f"https://scratch.mit.edu/users/{self.username}/")
            soup = BeautifulSoup(resp.text, "html.parser")

            details = soup.find("p", {"class": "profile-details"})
            if details is None:
                # No details, e.g. if the user is banned
                return None

            assert isinstance(details, Tag)

            class_name, class_id, is_closed = None, None, False
            for a in details.find_all("a"):
                if not isinstance(a, Tag):
                    continue
                href = str(a.get("href"))
                if re.match(r"/classes/\d*/", href):
                    class_name = a.text.strip()[len("Student of: "):]
                    is_closed = bool(re.search(r"\n *\(ended\)", class_name))# as this has a \n, we can be sure
                    if is_closed:
                        class_name = re.sub(r"\n *\(ended\)", "", class_name).strip()

                    class_id = int(href.split('/')[2])
                    break

            if class_name:
                self._classroom = True, classroom.Classroom(
                    _session=self._session,
                    id=class_id or 0,
                    title=class_name,
                    is_closed=is_closed
                )
            else:
                self._classroom = True, None

        return self._classroom[1]

    def does_exist(self) -> Optional[bool]:
        """
        Returns:
            boolean : True if the user exists, False if the user is deleted, None if an error occured
        """
        with requests.no_error_handling():
            status_code = requests.get(f"https://scratch.mit.edu/users/{self.username}/").status_code
            if status_code == 200:
                return True
            elif status_code == 404:
                return False

        return None


    # Will maybe be deprecated later, but for now still has its own purpose.
    #@deprecated("This function is partially deprecated. Use user.rank() instead.")
    def is_new_scratcher(self):
        """
        Returns:
            boolean : True if the user has the New Scratcher status, else False
        """
        try:
            with requests.no_error_handling():
                res = requests.get(f"https://scratch.mit.edu/users/{self.username}/").text
                group = res[res.rindex('<span class="group">'):][:70]
                return "new scratcher" in group.lower()

        except Exception as e:
            warnings.warn(f"Caught exception {e=}")
            return None

    def message_count(self):
        return json.loads(requests.get(f"https://api.scratch.mit.edu/users/{self.username}/messages/count/?cachebust={random.randint(0,10000)}", headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.3c6 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',}).text)["count"]

    def featured_data(self):
        """
        Returns:
            dict: Gets info on the user's featured project and featured label (like "Featured project", "My favorite things", etc.)
        """
        try:
            response = requests.get(f"https://scratch.mit.edu/site-api/users/all/{self.username}/").json()
            return {
                "label":response["featured_project_label_name"],
                "project":
                        dict(
                            id=str(response["featured_project_data"]["id"]),
                            author=response["featured_project_data"]["creator"],
                            thumbnail_url="https://"+response["featured_project_data"]["thumbnail_url"][2:],
                            title=response["featured_project_data"]["title"]
                        )
                    }
        except Exception:
            return None

    def unfollowers(self) -> list[User]:
        """
        Get all unfollowers by comparing API response and HTML response.
        NOTE: This method can take a long time to run.

        Based on https://juegostrower.github.io/unfollowers/
        """
        follower_count = self.follower_count()

        # regular followers
        usernames = []
        for i in range(1, 2 + follower_count // 60):
            with requests.no_error_handling():
                resp = requests.get(f"https://scratch.mit.edu/users/{self.username}/followers/", params={"page": i})
            soup = BeautifulSoup(resp.text, "html.parser")
            usernames.extend(span.text.strip() for span in soup.select("span.title"))

        # api response contains all-time followers, including deleted and unfollowed
        unfollowers = []
        for offset in range(0, follower_count, 40):
            unfollowers.extend(user for user in self.followers(offset=offset, limit=40) if user.username not in usernames)

        return unfollowers

    def unfollower_usernames(self) -> list[str]:
        return [user.username for user in self.unfollowers()]

    def follower_count(self):
        with requests.no_error_handling():
            text = requests.get(
                f"https://scratch.mit.edu/users/{self.username}/followers/",
                headers = self._headers
            ).text
            return commons.webscrape_count(text, "Followers (", ")")

    def following_count(self):
        with requests.no_error_handling():
            text = requests.get(
                f"https://scratch.mit.edu/users/{self.username}/following/",
                headers = self._headers
            ).text
            return commons.webscrape_count(text, "Following (", ")")

    def followers(self, *, limit=40, offset=0):
        """
        Returns:
            list<scratchattach.user.User>: The user's followers as list of scratchattach.user.User objects
        """
        response = commons.api_iterative(
            f"https://api.scratch.mit.edu/users/{self.username}/followers/", limit=limit, offset=offset)
        return commons.parse_object_list(response, User, self._session, "username")

    def follower_names(self, *, limit=40, offset=0):
        """
        Returns:
            list<str>: The usernames of the user's followers
        """
        return [i.name for i in self.followers(limit=limit, offset=offset)]

    def following(self, *, limit=40, offset=0):
        """
        Returns:
            list<scratchattach.user.User>: The users that the user is following as list of scratchattach.user.User objects
        """
        response = commons.api_iterative(
            f"https://api.scratch.mit.edu/users/{self.username}/following/", limit=limit, offset=offset)
        return commons.parse_object_list(response, User, self._session, "username")

    def following_names(self, *, limit=40, offset=0):
        """
        Returns:
            list<str>: The usernames of the users the user is following
        """
        return [i.name for i in self.following(limit=limit, offset=offset)]

    def is_following(self, user: str):
        """
        Returns:
            boolean: Whether the user is following the user provided as argument
        """
        offset = 0
        following = False

        while True:
            try:
                following_names = self.following_names(limit=20, offset=offset)
                if user in following_names:
                    following = True
                    break
                if not following_names:
                    break
                offset += 20
            except Exception as e:
                print(f"Warning: API error when performing following check: {e=}")
                return following
        return following

    def is_followed_by(self, user):
        """
        Returns:
            boolean: Whether the user is followed by the user provided as argument
        """
        offset = 0
        followed = False

        while True:
            try:
                followed_names = self.follower_names(limit=20, offset=offset)
                if user in followed_names:
                    followed = True
                    break
                if not followed_names:
                    break
                offset += 20
            except Exception as e:
                print(f"Warning: API error when performing following check: {e=}")
                return followed
        return followed

    def project_count(self):
        with requests.no_error_handling():
            text = requests.get(
                f"https://scratch.mit.edu/users/{self.username}/projects/",
                headers = self._headers
            ).text
            return commons.webscrape_count(text, "Shared Projects (", ")")

    def studio_count(self):
        with requests.no_error_handling():
            text = requests.get(
                f"https://scratch.mit.edu/users/{self.username}/studios/",
                headers = self._headers
            ).text
            return commons.webscrape_count(text, "Studios I Curate (", ")")

    def studios_following_count(self):
        with requests.no_error_handling():
            text = requests.get(
                f"https://scratch.mit.edu/users/{self.username}/studios_following/",
                headers = self._headers
            ).text
            return commons.webscrape_count(text, "Studios I Follow (", ")")

    def studios(self, *, limit=40, offset=0) -> list[studio.Studio]:
        _studios = commons.api_iterative(
            f"https://api.scratch.mit.edu/users/{self.username}/studios/curate", limit=limit, offset=offset)
        studios = []
        for studio_dict in _studios:
            _studio = studio.Studio(_session = self._session, id = studio_dict["id"])
            _studio._update_from_dict(studio_dict)
            studios.append(_studio)
        return studios

    def projects(self, *, limit=40, offset=0) -> list[project.Project]:
        """
        Returns:
            list<projects.projects.Project>: The user's shared projects
        """
        _projects = commons.api_iterative(
            f"https://api.scratch.mit.edu/users/{self.username}/projects/", limit=limit, offset=offset, _headers= self._headers)
        for p in _projects:
            p["author"] = {"username":self.username}
        return commons.parse_object_list(_projects, project.Project, self._session)

    def loves(self, *, limit=40, offset=0, get_full_project: bool = False) -> list[project.Project]:
        """
        Returns:
            list<projects.projects.Project>: The user's loved projects
        """
        # We need to use beautifulsoup webscraping so we cant use the api_iterative function
        if offset < 0:
            raise exceptions.BadRequest("offset parameter must be >= 0")
        if limit < 0:
            raise exceptions.BadRequest("limit parameter must be >= 0")

        # There are 40 projects on display per page
        # So the first page you need to view is 1 + offset // 40
        # (You have to add one because the first page is idx 1 instead of 0)

        # The final project to view is at idx offset + limit - 1
        # (You have to -1 because the index starts at 0)
        # So the page number for this is 1 + (offset + limit - 1) // 40

        # But this is a range so we have to add another 1 for the second argument
        pages = range(1 + offset // 40,
                      2 + (offset + limit - 1) // 40)
        _projects = []

        for page in pages:
            # The index of the first project on page #n is just (n-1) * 40
            first_idx = (page - 1) * 40

            with requests.no_error_handling():
                page_content = requests.get(f"https://scratch.mit.edu/projects/all/{self.username}/loves/"
                                            f"?page={page}", headers=self._headers).content

            soup = BeautifulSoup(
                page_content,
                "html.parser"
            )

            # We need to check if we are out of bounds
            # If we are, we can jump out early
            # This is detectable if Scratch gives you a '404'

            # We can't just detect if the 404 text is within the whole of the page content
            # because it would break if someone made a project with that name

            # This page only uses <h1> tags for the 404 text, so we can just use a soup for those
            h1_tag = soup.find("h1")
            if h1_tag is not None:
                # Just to confirm that it's a 404, in case I am wrong. It can't hurt
                if "Whoops! Our server is Scratch'ing its head" in h1_tag.text:
                    break

            # Each project element is a list item with the class name 'project thumb item' so we can just use that
            for i, project_element in enumerate(
                    soup.find_all("li", {"class": "project thumb item"})):
                # Remember we only want certain projects:
                # The current project idx = first_idx + i
                # We want to start at {offset} and end at {offset + limit}

                # So the offset <= current project idx <= offset + limit
                if offset <= first_idx + i <= offset + limit:
                    # Each of these elements provides:
                    # A project id
                    # A thumbnail link (no need to webscrape this)
                    # A title
                    # An Author (called an owner for some reason)
                    assert isinstance(project_element, Tag)
                    project_anchors = project_element.find_all("a")
                    # Each list item has three <a> tags, the first two linking the project
                    # 1st contains <img> tag
                    # 2nd contains project title
                    # 3rd links to the author & contains their username

                    # This function is pretty handy!
                    # I'll use it for an id from a string like: /projects/1070616180/
                    first_anchor = project_anchors[0]
                    second_anchor = project_anchors[1]
                    third_anchor = project_anchors[2]
                    assert isinstance(first_anchor, Tag)
                    assert isinstance(second_anchor, Tag)
                    assert isinstance(third_anchor, Tag)
                    project_id = commons.webscrape_count(first_anchor.attrs["href"],
                                                         "/projects/", "/")
                    title = second_anchor.contents[0]
                    author = third_anchor.contents[0]

                    # Instantiating a project with the properties that we know
                    # This may cause issues (see below)
                    _project = project.Project(id=project_id,
                                               _session=self._session,
                                               title=title,
                                               author_name=author,
                                               url=f"https://scratch.mit.edu/projects/{project_id}/")
                    if get_full_project:
                        # Put this under an if statement since making api requests for every single
                        # project will cause the function to take a lot longer
                        _project.update()

                    _projects.append(
                        _project
                    )

        return _projects

    def loves_count(self):
        with requests.no_error_handling():
            text = requests.get(
                f"https://scratch.mit.edu/projects/all/{self.username}/loves/",
                headers=self._headers
            ).text

        # If there are no loved projects, then Scratch doesn't actually display the number - so we have to catch this
        soup = BeautifulSoup(text, "html.parser")

        if not soup.find("li", {"class": "project thumb item"}):
            # There are no projects, so there are no projects loved
            return 0

        return commons.webscrape_count(text, "&raquo;\n\n (", ")")

    def favorites(self, *, limit=40, offset=0):
        """
        Returns:
            list<projects.projects.Project>: The user's favorite projects
        """
        _projects = commons.api_iterative(
            f"https://api.scratch.mit.edu/users/{self.username}/favorites/", limit=limit, offset=offset, _headers= self._headers)
        return commons.parse_object_list(_projects, project.Project, self._session)

    def favorites_count(self):
        with requests.no_error_handling():
            text = requests.get(
                f"https://scratch.mit.edu/users/{self.username}/favorites/",
                headers=self._headers
            ).text
        return commons.webscrape_count(text, "Favorites (", ")")

    def toggle_commenting(self):
        """
        You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_user`
        """
        self._assert_permission()
        requests.post(f"https://scratch.mit.edu/site-api/comments/user/{self.username}/toggle-comments/",
            headers = headers,
            cookies = self._cookies
        )

    def viewed_projects(self, limit=24, offset=0):
        """
        Returns:
            list<projects.projects.Project>: The user's recently viewed projects

        You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_user`
        """
        self._assert_permission()
        _projects = commons.api_iterative(
            f"https://api.scratch.mit.edu/users/{self.username}/projects/recentlyviewed", limit=limit, offset=offset, _headers= self._headers)
        return commons.parse_object_list(_projects, project.Project, self._session)

    def set_pfp(self, image: bytes):
        """
        Sets the user's profile picture. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_user`
        """
        # Teachers can set pfp! - Should update this method to check for that
        # self._assert_permission()
        requests.post(
            f"https://scratch.mit.edu/site-api/users/all/{self.username}/",
            headers=self._headers,
            cookies=self._cookies,
            files={"file": image})

    def set_bio(self, text):
        """
        Sets the user's "About me" section. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_user`
        """
        # Teachers can set bio! - Should update this method to check for that
        # self._assert_permission()
        requests.put(
            f"https://scratch.mit.edu/site-api/users/all/{self.username}/",
            headers=self._json_headers,
            cookies=self._cookies,
            json={"bio": text})

    def set_wiwo(self, text):
        """
        Sets the user's "What I'm working on" section. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_user`
        """
        # Teachers can also change your wiwo
        # self._assert_permission()
        requests.put(
            f"https://scratch.mit.edu/site-api/users/all/{self.username}/",
            headers=self._json_headers,
            cookies=self._cookies,
            json={"status": text})

    def set_featured(self, project_id, *, label=""):
        """
        Sets the user's featured project. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_user`

        Args:
            project_id: Project id of the project that should be set as featured

        Keyword Args:
            label: The label that should appear above the featured project on the user's profile (Like "Featured project", "Featured tutorial", "My favorite things", etc.)
        """
        self._assert_permission()
        requests.put(
            f"https://scratch.mit.edu/site-api/users/all/{self.username}/",
            headers=self._json_headers,
            cookies=self._cookies,
            json={"featured_project": int(project_id), "featured_project_label": label}
        )

    def set_forum_signature(self, text):
        """
        Sets the user's discuss forum signature. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_user`
        """
        self._assert_permission()
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://scratch.mit.edu',
            'referer': 'https://scratch.mit.edu/discuss/settings/TimMcCool/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        }
        data = {
            'csrfmiddlewaretoken': 'a',
            'signature': text,
            'update': '',
        }
        response = requests.post(f'https://scratch.mit.edu/discuss/settings/{self.username}/', cookies=self._cookies, headers=headers, data=data)

    def post_comment(self, content, *, parent_id="", commentee_id=""):
        """
        Posts a comment on the user's profile. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_user`

        Args:
            :param content: Content of the comment that should be posted

        Keyword Arguments:
            :param commentee_id: ID of the comment you want to reply to. If you don't want to mention a user, don't put the argument.
            :param parent_id: ID of the user that will be mentioned in your comment and will receive a message about your comment. If you don't want to mention a user, don't put the argument.

        Returns:
            scratchattach.comment.Comment: An object representing the created comment.
        """
        self._assert_auth()
        data = {
                "commentee_id": commentee_id,
                "content": str(content),
                "parent_id": parent_id,
        }
        r = requests.post(
            f"https://scratch.mit.edu/site-api/comments/user/{self.username}/add/",
            headers=headers,
            cookies=self._cookies,
            data=json.dumps(data),
        )
        if r.status_code != 200:
            if "Looks like we are having issues with our servers!" in r.text:
                raise exceptions.BadRequest("Invalid arguments passed")
            else:
                raise exceptions.CommentPostFailure(r.text)

        text = r.text
        try:
            data = {
                'id': text.split('<div id="comments-')[1].split('" class="comment')[0],
                'author': {"username": text.split('" data-comment-user="')[1].split('"><img class')[0]},
                'content': text.split('<div class="content">')[1].split('</div>')[0].strip(),
                'reply_count': 0,
                'cached_replies': []
            }
            _comment = comment.Comment(source=comment.CommentSource.USER_PROFILE, parent_id=None if parent_id=="" else parent_id, commentee_id=commentee_id, source_id=self.username, id=data["id"], _session = self._session, datetime = datetime.now())
            _comment._update_from_dict(data)
            return _comment
        except Exception as e:
            if '{"error": "isFlood"}' in text:
                raise(exceptions.CommentPostFailure(
                    "You are being rate-limited for running this operation too often. Implement a cooldown of about 10 seconds.")) from e
            elif '<script id="error-data" type="application/json">' in text:
                raw_error_data = text.split('<script id="error-data" type="application/json">')[1].split('</script>')[0]
                error_data = json.loads(raw_error_data)
                expires = error_data['mute_status']['muteExpiresAt']
                expires = datetime.fromtimestamp(expires, timezone.utc)
                raise(exceptions.CommentPostFailure(f"You have been muted. Mute expires on {expires}")) from e
            else:
                raise(exceptions.FetchError(f"Couldn't parse API response: {r.text!r}")) from e

    def reply_comment(self, content, *, parent_id, commentee_id=""):
        """
        Replies to a comment given by its id

        Warning:
            Only replies to top-level comments are shown on the Scratch website. Replies to replies are actually replies to the corresponding top-level comment in the API.

            Therefore, parent_id should be the comment id of a top level comment.

        Args:
            :param content: Content of the comment that should be posted

        Keyword Arguments:
            :param parent_id: ID of the comment you want to reply to
            :param commentee_id: ID of the user that will be mentioned in your comment and will receive a message about your comment. If you don't want to mention a user, don't put the argument.
        """
        return self.post_comment(content, parent_id=parent_id, commentee_id=commentee_id)

    def activity(self, *, limit=1000):
        """
        Returns:
            list<scratchattach.Activity>: The user's activity data as parsed list of scratchattach.activity.Activity objects
        """
        with requests.no_error_handling():
            soup = BeautifulSoup(requests.get(f"https://scratch.mit.edu/messages/ajax/user-activity/?user={self.username}&max={limit}").text, 'html.parser')

        activities = []
        source = soup.find_all("li")

        for data in source:
            _activity = activity.Activity(_session = self._session, raw=data)
            _activity._update_from_html(data)
            activities.append(_activity)

        return activities


    def activity_html(self, *, limit=1000):
        """
        Returns:
            str: The raw user activity HTML data
        """
        with requests.no_error_handling():
            return requests.get(f"https://scratch.mit.edu/messages/ajax/user-activity/?user={self.username}&max={limit}").text


    def follow(self):
        """
        Follows the user represented by the User object. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_user`
        """
        self._assert_auth()
        requests.put(
            f"https://scratch.mit.edu/site-api/users/followers/{self.username}/add/?usernames={self._session._username}",
            headers = headers,
            cookies = self._cookies,
        )

    def unfollow(self):
        """
        Unfollows the user represented by the User object. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_user`
        """
        self._assert_auth()
        requests.put(
            f"https://scratch.mit.edu/site-api/users/followers/{self.username}/remove/?usernames={self._session._username}",
            headers = headers,
            cookies = self._cookies,
        )

    def delete_comment(self, *, comment_id):
        """
        Deletes a comment by its ID. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_user`

        Args:
            comment_id: The id of the comment that should be deleted
        """
        self._assert_permission()
        with requests.no_error_handling():
            return requests.post(
                f"https://scratch.mit.edu/site-api/comments/user/{self.username}/del/",
                headers = headers,
                cookies = self._cookies,
                data = json.dumps({"id":str(comment_id)})
            )

    def report_comment(self, *, comment_id):
        """
        Reports a comment by its ID to the Scratch team. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_user`

        Args:
            comment_id: The id of the comment that should be reported
        """
        self._assert_auth()
        return requests.post(
            f"https://scratch.mit.edu/site-api/comments/user/{self.username}/rep/",
            headers = headers,
            cookies = self._cookies,
            data = json.dumps({"id":str(comment_id)})
        )

    def comments(self, *, page=1, limit=None) -> list[comment.Comment]:
        """
        Returns the comments posted on the user's profile (with replies).

        Keyword Arguments:
            page: The page of the comments that should be returned.
            limit: Max. amount of returned comments.

        Returns:
            list<scratchattach.comment.Comment>: A list containing the requested comments as Comment objects.
        """
        URL = f"https://scratch.mit.edu/site-api/comments/user/{self.username}/?page={page}"
        DATA = []

        with requests.no_error_handling():
            page_contents = requests.get(URL).content

        soup = BeautifulSoup(page_contents, "html.parser")

        _comments = soup.find_all("li", {"class": "top-level-reply"})

        if len(_comments) == 0:
            return []

        for entity in _comments:
            comment_id = entity.find("div", {"class": "comment"})['data-comment-id']
            user = entity.find("a", {"id": "comment-user"})['data-comment-user']
            content = str(entity.find("div", {"class": "content"}).text).strip()
            time = entity.find("span", {"class": "time"})['title']

            main_comment = {
                'id': comment_id,
                'author': {"username":user},
                'content': content,
                'datetime_created': time,
            }
            _comment = comment.Comment(source=comment.CommentSource.USER_PROFILE, source_id=self.username, _session = self._session)
            _comment._update_from_dict(main_comment)

            ALL_REPLIES = []
            replies = entity.find_all("li", {"class": "reply"})
            if len(replies) > 0:
                hasReplies = True
            else:
                hasReplies = False
            for reply in replies:
                r_comment_id = reply.find("div", {"class": "comment"})['data-comment-id']
                r_user = reply.find("a", {"id": "comment-user"})['data-comment-user']
                r_content = str(reply.find("div", {"class": "content"}).text).strip().replace("\n", "").replace(
                    "                    ", " ")
                r_time = reply.find("span", {"class": "time"})['title']
                reply_data = {
                    'id': r_comment_id,
                    'author': {'username': r_user},
                    'content': r_content,
                    'datetime_created': r_time,
                    "parent_id": comment_id,
                    "cached_parent_comment": _comment,
                }
                _r_comment = comment.Comment(source=comment.CommentSource.USER_PROFILE, source_id=self.username, _session = self._session, cached_parent_comment=_comment)
                _r_comment._update_from_dict(reply_data)
                ALL_REPLIES.append(_r_comment)

            _comment.reply_count = len(ALL_REPLIES)
            _comment.cached_replies = list(ALL_REPLIES)

            DATA.append(_comment)
        return DATA

    def comment_by_id(self, comment_id) -> comment.Comment:
        """
        Gets a comment on this user's profile by id.

        Warning:
            For comments very far down on the user's profile, this method will take a while to find the comment. Very old comment are deleted from Scratch's database and may not appear.

        Returns:
            scratchattach.comments.Comment: The request comment.
        """

        page = 1
        page_content = self.comments(page=page)
        while page_content != []:
            results = list(filter(lambda x : str(x.id) == str(comment_id), page_content))
            if results == []:
                results = list(filter(lambda x : str(x.id) == str(comment_id), [item for x in page_content for item in x.cached_replies]))
                if results != []:
                    return results[0]
            else:
                return results[0]
            page += 1
            page_content = self.comments(page=page)
        raise exceptions.CommentNotFound()

    def message_events(self):
        return message_events.MessageEvents(self)

    @deprecated("This method is deprecated because ScratchDB is down indefinitely.")
    def stats(self):
        """
        Gets information about the user's stats. Fetched from ScratchDB.

        Warning:
            ScratchDB is down indefinitely, therefore this method is deprecated.

        Returns:
            dict: A dict containing the user's stats. If the stats aren't available, all values will be -1.
        """
        try:
            stats= requests.get(
                f"https://scratchdb.lefty.one/v3/user/info/{self.username}"
            ).json()["statistics"]
            stats.pop("ranks")
        except Exception:
            stats = {"loves":-1,"favorites":-1,"comments":-1,"views":-1,"followers":-1,"following":-1}
        return stats

    @deprecated("Warning: ScratchDB is down indefinitely, therefore this method is deprecated.")
    def ranks(self):
        """
        Gets information about the user's ranks. Fetched from ScratchDB.

        Warning:
            ScratchDB is down indefinitely, therefore this method is deprecated.

        Returns:
            dict: A dict containing the user's ranks. If the ranks aren't available, all values will be -1.
        """
        try:
            return requests.get(
                f"https://scratchdb.lefty.one/v3/user/info/{self.username}"
            ).json()["statistics"]["ranks"]
        except Exception:
            return {"country":{"loves":0,"favorites":0,"comments":0,"views":0,"followers":0,"following":0},"loves":0,"favorites":0,"comments":0,"views":0,"followers":0,"following":0}

    def ocular_status(self) -> _OcularStatus:
        """
        Gets information about the user's ocular status. Ocular is a website developed by jeffalo: https://ocular.jeffalo.net/

        Returns:
            dict
        """
        return requests.get(f"https://my-ocular.jeffalo.net/api/user/{self.username}").json()

    def verify_identity(self, *, verification_project_id=395330233):
        """
        Can be used in applications to verify a user's identity.

        This function returns a Verifactor object. Attributs of this object:
        :.projecturl: The link to the project where the user has to go to verify
        :.project: The project where the user has to go to verify as scratchattach.Project object
        :.code: The code that the user has to comment

        To check if the user verified successfully, call the .check() function on the returned object.
        It will return True if the user commented the code.
        """

        v = Verificator(self, verification_project_id)
        return v

    def rank(self) -> Rank:
        """
        Finds the rank of the user.
        Returns a member of the Rank enum: either Rank.NEW_SCRATCHER, Rank.SCRATCHER, or Rank.SCRATCH_TEAM.
        May replace user.scratchteam and user.is_new_scratcher in the future.
        """

        if self.is_new_scratcher():
            return Rank.NEW_SCRATCHER
        
        if not self.scratchteam:
            return Rank.SCRATCHER

        return Rank.SCRATCH_TEAM


# ------ #

def get_user(username) -> User:
    """
    Gets a user without logging in.

    Args:
        username (str): Username of the requested user

    Returns:
        scratchattach.user.User: An object representing the requested user

    Warning:
        Any methods that require authentication (like user.follow) will not work on the returned object.

        If you want to use these, get the user with :meth:`scratchattach.session.Session.connect_user` instead.
    """
    warnings.warn(
        "Warning: For methods that require authentication, use session.connect_user instead of get_user.\n"
        "To ignore this warning, use warnings.filterwarnings('ignore', category=scratchattach.UserAuthenticationWarning).\n"
        "To ignore all warnings of the type GetAuthenticationWarning, which includes this warning, use "
        "`warnings.filterwarnings('ignore', category=scratchattach.GetAuthenticationWarning)`.",
        exceptions.UserAuthenticationWarning
    )
    return commons._get_object("username", username, User, exceptions.UserNotFound)
