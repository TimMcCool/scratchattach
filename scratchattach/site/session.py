"""v2 ready: Session class and login function"""

import json
import re
import requests
import warnings
import pathlib
import hashlib
import time
import random

from . import forum

from ..utils import commons

from . import user
from ..cloud import cloud
from . import project
from .. import exceptions
from . import studio
from ..eventhandlers import message_events
from . import activity
from ._base import BaseSiteComponent
from ..utils.commons import headers, empty_project_json
from bs4 import BeautifulSoup

CREATE_PROJECT_USES = []

class Session(BaseSiteComponent):

    '''
    Represents a Scratch log in / session. Stores authentication data (session id and xtoken).

    Attributes:

    :.session_id: The session id associated with the login

    :.username: The username associated with the login

    :.xtoken: The xtoken associated with the login

    :.email: The email address associated with the logged in account

    :.new_scratcher: Returns True if the associated account is a Scratcher

    :.mute_status: Information about commenting restrictions of the associated account

    :.banned: Returns True if the associated account is banned
    '''

    def __str__(self):
        return "Login for account: {self.username}"

    def __init__(self, **entries):

        # Info on how the .update method has to fetch the data:
        self.update_function = requests.post
        self.update_API = "https://scratch.mit.edu/session"

        # Set attributes every Session object needs to have:
        self.session_id = None
        self.username = None
        self.xtoken = None
        self.new_scratcher = None

        # Update attributes from entries dict:
        self.__dict__.update(entries)

        # Set alternative attributes:
        self._username = self.username # backwards compatibility with v1

        # Base headers and cookies of every session:
        self._headers = headers
        self._cookies = {
            "scratchsessionsid" : self.session_id,
            "scratchcsrftoken" : "a",
            "scratchlanguage" : "en",
            "accept": "application/json",
            "Content-Type": "application/json",
        }

    def _update_from_dict(self, data):
        self.xtoken = data['user']['token']
        self._headers["X-Token"] = self.xtoken
        self.email = data["user"]["email"]
        self.new_scratcher = data["permissions"]["new_scratcher"]
        self.mute_status = data["permissions"]["mute_status"]
        self.username = data["user"]["username"]
        self._username = data["user"]["username"]
        self.banned = data["user"]["banned"]
        if self.banned:
            warnings.warn(f"Warning: The account {self._username} you logged in to is BANNED. Some features may not work properly.")
        return True

    def connect_linked_user(self):
        '''
        Gets the user associated with the log in / session.

        Warning:
            The returned User object is cached. To ensure its attribute are up to date, you need to run .update() on it.

        Returns:
            scratchattach.user.User: Object representing the user associated with the log in / session.
        '''
        if not hasattr(self, "_user"):
            self._user = self.connect_user(self._username)
        return self._user

    def get_linked_user(self):
        # backwards compatibility with v1
        return self.connect_linked_user() # To avoid inconsistencies with "connect" and "get", this function was renamed

    def messages(self, *, limit=40, offset=0):
        '''
        Returns the messages.

        Returns:
            list<dict>: List that contains all messages as dicts.
        '''
        data = commons.api_iterative(
            f"https://api.scratch.mit.edu/users/{self._username}/messages",
            limit = limit, offset = offset, headers = self._headers, cookies = self._cookies
        )
        return commons.parse_object_list(data, activity.Activity, self)

    def clear_messages(self):
        '''
        Clears all messages.
        '''
        return requests.post(
            "https://scratch.mit.edu/site-api/messages/messages-clear/",
            headers = self._headers,
            cookies = self._cookies,
            timeout = 10,
        ).text

    def message_count(self):
        '''
        Returns the message count.

        Returns:
            int: message count
        '''
        return json.loads(requests.get(
            f"https://scratch.mit.edu/messages/ajax/get-message-count/",
            headers = self._headers,
            cookies = self._cookies,
            timeout = 10,
        ).text)["msg_count"]

    # Front-page-related stuff:

    def feed(self, *, limit=20, offset=0):
        '''
        Returns the "What's happening" section (frontpage).

        Returns:
            list<dict>: List that contains all "What's happening" entries as dicts
        '''
        data = commons.api_iterative(
            f"https://api.scratch.mit.edu/users/{self._username}/following/users/activity",
            limit = limit, offset = offset, headers = self._headers, cookies = self._cookies
        )
        return commons.parse_object_list(data, activity.Activity, self)

    def get_feed(self, *, limit=20, offset=0):
        # for more consistent names, this method was renamed
        return self.feed(limit=limit, offset=offset) # for backwards compatibility with v1

    def loved_by_followed_users(self, *, limit=40, offset=0):
        '''
        Returns the "Projects loved by Scratchers I'm following" section (frontpage).

        Returns:
            list<scratchattach.project.Project>: List that contains all "Projects loved by Scratchers I'm following" entries as Project objects
        '''
        data = commons.api_iterative(
            f"https://api.scratch.mit.edu/users/{self._username}/following/users/loves",
            limit = limit, offset = offset, headers = self._headers, cookies = self._cookies
        )
        return commons.parse_object_list(data, project.Project, self)

    # Search:

    def search_projects(self, *, query="", mode="trending", language="en", limit=40, offset=0):
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
        response = commons.api_iterative(
            f"https://api.scratch.mit.edu/search/projects", limit=limit, offset=offset, add_params=f"&language={language}&mode={mode}&q={query}")
        return commons.parse_object_list(response, project.Project, self)

    def explore_projects(self, *, query="*", mode="trending", language="en", limit=40, offset=0):
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
        response = commons.api_iterative(
            f"https://api.scratch.mit.edu/explore/projects", limit=limit, offset=offset, add_params=f"&language={language}&mode={mode}&q={query}")
        return commons.parse_object_list(response, project.Project, self)

    def search_studios(self, *, query="", mode="trending", language="en", limit=None, offset=0):
        if not query:
            raise ValueError("The query can't be empty for search")
        response = commons.api_iterative(
            f"https://api.scratch.mit.edu/search/studios", limit=limit, offset=offset, add_params=f"&language={language}&mode={mode}&q={query}")
        return commons.parse_object_list(response, studio.Studio, self)


    def explore_studios(self, *, query="", mode="trending", language="en", limit=None, offset=0):
        if not query:
            raise ValueError("The query can't be empty for explore")
        response = commons.api_iterative(
            f"https://api.scratch.mit.edu/explore/studios", limit=limit, offset=offset, add_params=f"&language={language}&mode={mode}&q={query}")
        return commons.parse_object_list(response, studio.Studio, self)


    def create_project(self, *, title=None, project_json=empty_project_json, parent_id=None): # not working
        """
        Creates a project on the Scratch website.

        Warning:
            Don't spam this method - it WILL get you banned from Scratch.
            To prevendfvt accidental spam, a rate limit (5 projects per minute) is implemented for this function.
        """
        global CREATE_PROJECT_USES
        if len(CREATE_PROJECT_USES) < 5:
            CREATE_PROJECT_USES.insert(0, time.time())
        else:
            if CREATE_PROJECT_USES[-1] < time.time() - 300:
                CREATE_PROJECT_USES.pop()
            else:
                raise exceptions.BadRequest("Rate limit for creating Scratch projects exceeded.\nThis rate limit is enforced by scratchattach, not by the Scratch API.\nFor security reasons, it cannot be turned off.\n\nDon't spam-create projects, it WILL get you banned.")
                return
            CREATE_PROJECT_USES.insert(0, time.time())

        if title is None:
            title = f'Untitled-{random.randint(0, 200)}'

        params = {
            'is_remix': '0' if parent_id is None else "1",
            'original_id': parent_id,
            'title': title,
        }

        response = requests.post('https://projects.scratch.mit.edu/', params=params, cookies=self._cookies, headers=self._headers, json=project_json).json()
        return self.connect_project(response["content-name"])


    """ work in progress

    # My stuff:

    def mystuff_projects(self, ordering, *, page=1, sort_by="", descending=True):
        '''
        Gets the projects from the "My stuff" page.

        Args:
            ordering (str): Possible values for this parameter are "all", "shared", "unshared" and "trashed"

        Keyword Arguments:
            page (int): The page of the "My Stuff" projects that should be returned
            sort_by (str): The key the projects should be sorted based on. Possible values for this parameter are "" (then the projects are sorted based on last modified), "view_count", love_count", "remixers_count" (then the projects are sorted based on remix count) and "title" (then the projects are sorted based on title)
            descending (boolean): Determines if the element with the highest key value (the key is specified in the sort_by argument) should be returned first. Defaults to True.

        Returns:
            list<dict>: A list with the projects from the "My Stuff" page, each project is represented by a dict.
        '''
        if descending:
            ascsort = ""
            descsort = sort_by
        else:
            ascsort = sort_by
            descsort = ""
        try:
            targets = requests.get(
                f"https://scratch.mit.edu/site-api/projects/{ordering}/?page={page}&ascsort={ascsort}&descsort={descsort}",
                headers = headers,
                cookies = self._cookies,
                timeout = 10,
            ).json()
            projects = []
            for target in targets:
                projects.append(
                    project.Project(
                        author = self._username,
                        created = target["fields"]["datetime_created"],
                        last_modified = target["fields"]["datetime_modified"],
                        share_date = target["fields"]["datetime_shared"],
                        shared = target["fields"]["isPublished"],
                        id = target["pk"],
                        thumbnail_url = "https://uploads.scratch.mit.edu"+target["fields"]["uncached_thumbnail_url"][1:],
                        favorites = target["fields"]["favorite_count"],
                        loves = target["fields"]["love_count"],
                        remixes = target["fields"]["remixers_count"],
                        views = target["fields"]["view_count"],
                        thumbnail_name = target["fields"]["thumbnail"],
                        title = target["fields"]["title"],
                        url = "https://scratch.mit.edu/projects/" + str(target["pk"]),
                        comment_count = target["fields"]["commenters_count"],
                    )
                )
            return projects
        except Exception:
            raise(exceptions.FetchError)

    def get_mystuff_projects(self, ordering, *, page=1, sort_by="", descending=True):
        '''
        Outdated name for :meth:`scratchattach.session.Session.mystuff_projects`. See the documentation of this function.
        '''
        return self.mystuff_projects(ordering, page=page, sort_by=sort_by, descending=descending)

    def backpack(self,limit=20, offset=0):
        '''
        Lists the assets that are in the backpack of the user associated with the session.

        Returns:
            list<dict>: List that contains the backpack items as dicts
        '''
        return requests.get(
            f"https://backpack.scratch.mit.edu/{self._username}?limit={limit}&offset={offset}",
            headers = self._headers,
            timeout = 10,
        ).json()

    def delete_from_backpack(self, asset_id):
        '''
        Deletes an asset from the backpack.

        Args:
            asset_id: ID of the asset that will be deleted.
        '''
        return requests.delete(
            f"https://backpack.scratch.mit.edu/{self._username}/{asset_id}",
            headers = self._headers,
            timeout = 10,
        ).json()''

    def connect_cloud(self, project_id_arg=None, *, project_id=None):
        '''
        Connects to the cloud variables of a project.

        Args:
            project_id (str): ID of the project that will be connected to.

        Returns:
            scratchattach.cloud.CloudConnection: An object that represents the created connection and allows you to set cloud variables
        '''
        if project_id is None:
            project_id = project_id_arg
        if project_id is None:
            return None

        return cloud.CloudConnection(username = self._username, session_id = self.session_id, project_id = int(project_id))

    def connect_tw_cloud(self, project_id_arg=None, *, project_id=None, purpose="", contact=""):
        return cloud.connect_tw_cloud(project_id_arg, project_id=project_id, purpose=purpose, contact=contact)

    def search_posts(self, *, query, order="newest", page=0):
        try:
            data = requests.get(f"https://scratchdb.lefty.one/v3/forum/search?q={query}&o={order}&page={page}", timeout=10).json()["posts"]
            return_data = []
            for o in data:
                a = forum.ForumPost(id = o["id"], _session = self)
                a._update_from_dict(o)
                return_data.append(a)
            return return_data
        except Exception:
            return []

    def upload_asset(self, asset):
        data = asset if isinstance(asset, bytes) else open(asset, "rb").read()

        if isinstance(asset, str):
            file_ext = pathlib.Path(asset).suffix

        requests.post(
            f"https://assets.scratch.mit.edu/{hashlib.md5(data).hexdigest()}.{file_ext}",
            headers=self._headers,
            data=data,
            timeout=10,
        )

    def connect_topic_list(self, category_name, *, page=0, include_deleted=False):
        '''
        Gets the topics from a forum category.

        Args:
            category_name (str): Name of the forum category

        Keyword Arguments:
            page (str): Page of the category topics that should be returned
            include_deleted (boolean): Whether deleted topics should be returned too

        Returns:
            list<scratchattach.forum.ForumTopic>: A list containing the forum topics from the specified category
        '''
        category_name.replace(" ", "%20")
        if include_deleted:
            filter = 0
        else:
            filter = 1
        try:
            data = requests.get(f"https://scratchdb.lefty.one/v3/forum/category/topics/{category_name}/{page}?detail=1&filter={filter}", timeout=10).json()
            return_data = []
            for topic in data:
                t = forum.ForumTopic(id = topic["id"], _session=self)
                t._update_from_dict(topic)
                return_data.append(t)
            return return_data
        except Exception:
            return None
    """

    def _connect_object(self, identificator_id, identificator, Class, NotFoundException):
        # Interal function: Generalization of the process ran by connect_user, connect_studio etc.
        try:
            _object = Class(**{identificator_id:identificator, "_session":self})
            if _object.update() == "429":
                raise(exceptions.Response429("Your network is blocked or rate-limited by Scratch.\nIf you're using an online IDE like replit.com, try running the code on your computer."))
            if not _object: # Target is unshared
                return False
            return _object
        except KeyError as e:
            raise(NotFoundException("Key error at key "+str(e)+" when reading API response"))
        except Exception as e:
            raise(e)


    def connect_user(self, username):
        """
        Gets a user using this session, connects the session to the User object to allow authenticated actions

        Args:
            username (str): Username of the requested user

        Returns:
            scratchattach.user.User: An object that represents the requested user and allows you to perform actions on the user (like user.follow)
        """
        return self._connect_object("username", username, user.User, exceptions.UserNotFound)

    def find_username_from_id(self, user_id:int):
        """
        Warning:
            Every time this functions is run, a comment on your profile is posted and deleted. Therefore you shouldn't run this too often.

        Returns:
            str: The username that corresponds to the user id
        """
        you = user.User(username=self.username, _session=self)
        try:
            comment = you.post_comment("scratchattach", commentee_id=int(user_id))
        except exceptions.CommentPostFailure:
            raise exceptions.BadRequest("After posting a comment, you need to wait 10 seconds before you can connect users by id again.")
        except exceptions.BadRequest:
            raise exceptions.UserNotFound("Invalid user id")
        except Exception as e:
            raise e
        you.delete_comment(comment_id=comment.id)
        try:
            username = comment.content.split('">@')[1]
            username = username.split("</a>")[0]
        except IndexError:
            raise exceptions.UserNotFound()
        return username


    def connect_user_by_id(self, user_id:int):
        """
        Gets a user using this session, connects the session to the User object to allow authenticated actions

        This method ...
        1) gets the username by posting a comment with the user_id as commentee_id.
        2) deletes the posted comment.
        3) fetches other information about the user using Scratch's api.scratch.mit.edu/users/username API.

        Warning:
            Every time this functions is run, a comment on your profile is posted and deleted. Therefore you shouldn't run this too often.

        Args:
            user_id (int): User ID of the requested user

        Returns:
            scratchattach.user.User: An object that represents the requested user and allows you to perform actions on the user (like user.follow)
        """
        return self._connect_object("username", self.find_username_from_id(user_id), user.User, exceptions.UserNotFound)

    def connect_project(self, project_id):
        """
        Gets a project using this session, connects the session to the Project object to allow authenticated actions
sess
        Args:
            project_id (int): ID of the requested project

        Returns:
            scratchattach.project.Project: An object that represents the requested project and allows you to perform actions on the project (like project.love)
        """
        result = self._connect_object("id", int(project_id), project.Project, exceptions.ProjectNotFound)
        if result is False: # Project is unshared
            return project.PartialProject(id=int(project_id), _session=self._session)
        return result

    def connect_studio(self, studio_id):
        """
        Gets a studio using this session, connects the session to the Studio object to allow authenticated actions

        Args:
            studio_id (int): ID of the requested studio

        Returns:
            scratchattach.studio.Studio: An object that represents the requested studio and allows you to perform actions on the studio (like studio.follow)
        """
        return self._connect_object("id", int(studio_id), studio.Studio, exceptions.StudioNotFound)

    def connect_topic(self, topic_id):
        """
        Gets a forum topic using this session, connects the session to the ForumTopic object to allow authenticated actions

        Args:
            topic_id (int): ID of the requested forum topic (can be found in the browser URL bar)

        Returns:
            scratchattach.forum.ForumTopic: An object that represents the requested forum topic
        """
        return self._connect_object("id", int(topic_id), forum.ForumTopic, exceptions.ForumContentNotFound)

    def connect_post(self, post_id):

        """
        Gets a forum post using this session, connects the session to the ForumPost object to allow authenticated actions

        Args:
            post_id (int): ID of the requested forum post

        Returns:
            scratchattach.forum.ForumPost: An object that represents the requested forum post
        """
        return self._connect_object("id", int(post_id), forum.ForumPost, exceptions.ForumContentNotFound)

    def connect_message_events(self):
        return message_events.MessageEvents(user.User(username=self.username, _session=self))


# ------ #

def login_by_id(session_id, *, username=None):
    """
    Creates a session / log in to the Scratch website with the specified session id.
    Structured similarly to Session._connect_object method.

    Args:
        session_id (str)
        password (str)

    Keyword arguments:
        timeout (int): Optional, but recommended. Specify this when the Python environment's IP address is blocked by Scratch's API, but you still want to use cloud variables.

    Returns:
        scratchattach.session.Session: An object that represents the created log in / session
    """

    try:
        _session = Session(session_id=session_id, username=username)
        if _session.update() == "429":
            raise(exceptions.Response429("Your network is blocked or rate-limited by Scratch.\nIf you're using an online IDE like replit.com, try running the code on your computer."))
        return _session
    except KeyError as e:
        print(f"Warning: Logged in, but couldn't fetch XToken. Key error at key "+str(e)+" when reading scratch.mit.edu/session API response")
    except Exception as e:
        raise(e)

def login(username, password, *, timeout=10):
    """
    Creates a session / log in to the Scratch website with the specified username and password.

    This method ...
    1. creates a session id by posting a login request to Scratch's login API. (If this fails, scratchattach.exceptions.LoginFailure is raised)
    2. fetches the xtoken and other information by posting a request to scratch.mit.edu/session. (If this fails, a warning is displayed)

    Args:
        username (str)
        password (str)

    Keyword arguments:
        timeout (int): Timeout for the request to Scratch's login API (in seconds). Defaults to 10.

    Returns:
        scratchattach.session.Session: An object that represents the created log in / session
    """

    # Post request to login API:
    data = json.dumps({"username": username, "password": password})
    _headers = dict(headers)
    _headers["Cookie"] = "scratchcsrftoken=a;scratchlanguage=en;"
    request = requests.post(
        "https://scratch.mit.edu/login/", data=data, headers=_headers,
        timeout = timeout,
    )
    try:
        session_id = str(re.search('"(.*)"', request.headers["Set-Cookie"]).group())
    except Exception:
        raise exceptions.LoginFailure(
            "Either the provided authentication data is wrong or your network is banned from Scratch.\n\nIf you're using an online IDE (like replit.com) Scratch possibly banned its IP adress. In this case, try logging in with your session id: https://github.com/TimMcCool/scratchattach/wiki#logging-in")

    # Create session object:
    return login_by_id(session_id, username=username)
