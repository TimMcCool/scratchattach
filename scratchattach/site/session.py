"""Session class and login function"""

import base64
import hashlib
import json
import pathlib
import random
import re
import time
import warnings
from typing import Type

from bs4 import BeautifulSoup

from . import activity
from . import classroom
from . import forum
from . import studio
from . import user, project, backpack_asset
from ._base import BaseSiteComponent
from ..cloud import cloud, _base
from ..eventhandlers import message_events, filterbot
from ..other import project_json_capabilities
from ..utils import commons
from ..utils import exceptions
from ..utils.commons import headers, empty_project_json
from ..utils.requests import Requests as requests

CREATE_PROJECT_USES = []

class Session(BaseSiteComponent):

    '''
    Represents a Scratch log in / session. Stores authentication data (session id and xtoken).

    Attributes:

    :.id: The session id associated with the login

    :.username: The username associated with the login

    :.xtoken: The xtoken associated with the login

    :.email: The email address associated with the logged in account

    :.new_scratcher: Returns True if the associated account is a new Scratcher

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
        self.id = None
        self.username = None
        self.xtoken = None
        self.new_scratcher = None

        # Update attributes from entries dict:
        self.__dict__.update(entries)

        # Set alternative attributes:
        self._username = self.username # backwards compatibility with v1

        # Base headers and cookies of every session:
        self._headers = dict(headers)
        self._cookies = {
            "scratchsessionsid" : self.id,
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

    def delete_account(self, *, password: str, delete_projects: bool = False):
        """
        !!! Dangerous !!!
        Sends a request to delete the account that is associated with this session.
        You can cancel the deletion simply by logging back in (including using sa.login(username, password))

        Keyword arguments:
            password (str): The password associated with the account
            delete_projects (bool): Whether to delete all the projects as well
        """
        requests.post("https://scratch.mit.edu/accounts/settings/delete_account/",
                      data={
                          "delete_state": "delbyusrwproj" if delete_projects else "delbyusr",
                          "password": password
                      }, headers=self._headers, cookies=self._cookies)

    def messages(self, *, limit=40, offset=0, date_limit=None, filter_by=None):
        '''
        Returns the messages.

        Keyword arguments:
            limit, offset, date_limit
            filter_by (str or None): Can either be None (no filter), "comments", "projects", "studios" or "forums"

        Returns:
            list<scratch.activity.Activity>: List that contains all messages as Activity objects.
        '''
        add_params = ""
        if date_limit is not None:
            add_params += f"&dateLimit={date_limit}"
        if filter_by is not None:
            add_params += f"&filter={filter_by}"
        data = commons.api_iterative(
            f"https://api.scratch.mit.edu/users/{self._username}/messages",
            limit = limit, offset = offset, headers = self._headers, cookies = self._cookies, add_params=add_params
        )
        return commons.parse_object_list(data, activity.Activity, self)

    def admin_messages(self, *, limit=40, offset=0):
        """
        Returns your messages sent by the Scratch team (alerts).
        """
        return commons.api_iterative(
            f"https://api.scratch.mit.edu/users/{self._username}/messages/admin",
            limit = limit, offset = offset, headers = self._headers, cookies = self._cookies
        )


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

    def feed(self, *, limit=20, offset=0, date_limit=None):
        '''
        Returns the "What's happening" section (frontpage).

        Returns:
            list<scratch.activity.Activity>: List that contains all "What's happening" entries as Activity objects
        '''
        add_params = ""
        if date_limit is not None:
            add_params = f"&dateLimit={date_limit}"
        data = commons.api_iterative(
            f"https://api.scratch.mit.edu/users/{self._username}/following/users/activity",
            limit = limit, offset = offset, headers = self._headers, cookies = self._cookies, add_params=add_params
        )
        return commons.parse_object_list(data, activity.Activity, self)

    def get_feed(self, *, limit=20, offset=0, date_limit=None):
        # for more consistent names, this method was renamed
        return self.feed(limit=limit, offset=offset, date_limit=date_limit) # for backwards compatibility with v1

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

    """
    These methods are disabled because it is unclear if there is any case in which the response is not empty. 
    def shared_by_followed_users(self, *, limit=40, offset=0):
        '''
        Returns the "Projects by Scratchers I'm following" section (frontpage).
        This section is only visible to old accounts (according to the Scratch wiki).
        For newer users, this method will always return an empty list.

        Returns:
            list<scratchattach.project.Project>: List that contains all "Projects loved by Scratchers I'm following" entries as Project objects
        '''
        data = commons.api_iterative(
            f"https://api.scratch.mit.edu/users/{self._username}/following/users/projects",
            limit = limit, offset = offset, headers = self._headers, cookies = self._cookies
        )
        return commons.parse_object_list(data, project.Project, self)

    def in_followed_studios(self, *, limit=40, offset=0):
        '''
        Returns the "Projects in studios I'm following" section (frontpage).
        This section is only visible to old accounts (according to the Scratch wiki).
        For newer users, this method will always return an empty list.

        Returns:
            list<scratchattach.project.Project>: List that contains all "Projects loved by Scratchers I'm following" entries as Project objects
        '''
        data = commons.api_iterative(
            f"https://api.scratch.mit.edu/users/{self._username}/following/studios/projects",
            limit = limit, offset = offset, headers = self._headers, cookies = self._cookies
        )
        return commons.parse_object_list(data, project.Project, self)"""

    # -- Project JSON editing capabilities ---

    def connect_empty_project_pb():
        pb = project_json_capabilities.ProjectBody()
        pb.from_json(empty_project_json)
        return pb

    def connect_pb_from_dict(project_json:dict):
        pb = project_json_capabilities.ProjectBody()
        pb.from_json(project_json)
        return pb

    def connect_pb_from_file(path_to_file):
        pb = project_json_capabilities.ProjectBody()
        pb.from_json(project_json_capabilities._load_sb3_file(path_to_file))
        return pb

    def download_asset(asset_id_with_file_ext, *, filename=None, dir=""):
        if not (dir.endswith("/") or dir.endswith("\\")):
            dir = dir+"/"
        try:
            if filename is None:
                filename = str(asset_id_with_file_ext)
            response = requests.get(
                "https://assets.scratch.mit.edu/"+str(asset_id_with_file_ext),
                timeout=10,
            )
            open(f"{dir}{filename}", "wb").write(response.content)
        except Exception:
            raise (
                exceptions.FetchError(
                    "Failed to download asset"
                )
            )

    def upload_asset(self, asset_content, *, asset_id=None, file_ext=None):
        data = asset_content if isinstance(asset_content, bytes) else open(asset_content, "rb").read()

        if isinstance(asset_content, str):
            file_ext = pathlib.Path(asset_content).suffix

        if asset_id is None:
            asset_id = hashlib.md5(data).hexdigest()

        requests.post(
            f"https://assets.scratch.mit.edu/{asset_id}.{file_ext}",
            headers=self._headers,
            data=data,
            timeout=10,
        )

    # --- Search ---

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

    def search_studios(self, *, query="", mode="trending", language="en", limit=40, offset=0):
        if not query:
            raise ValueError("The query can't be empty for search")
        response = commons.api_iterative(
            f"https://api.scratch.mit.edu/search/studios", limit=limit, offset=offset, add_params=f"&language={language}&mode={mode}&q={query}")
        return commons.parse_object_list(response, studio.Studio, self)


    def explore_studios(self, *, query="", mode="trending", language="en", limit=40, offset=0):
        if not query:
            raise ValueError("The query can't be empty for explore")
        response = commons.api_iterative(
            f"https://api.scratch.mit.edu/explore/studios", limit=limit, offset=offset, add_params=f"&language={language}&mode={mode}&q={query}")
        return commons.parse_object_list(response, studio.Studio, self)


    # --- Create project API ---

    def create_project(self, *, title=None, project_json=empty_project_json, parent_id=None): # not working
        """
        Creates a project on the Scratch website.

        Warning:
            Don't spam this method - it WILL get you banned from Scratch.
            To prevent accidental spam, a rate limit (5 projects per minute) is implemented for this function.
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

    # --- My stuff page ---

    def mystuff_projects(self, filter_arg="all", *, page=1, sort_by="", descending=True):
        '''
        Gets the projects from the "My stuff" page.

        Args:
            filter_arg (str): Possible values for this parameter are "all", "shared", "unshared" and "trashed"

        Keyword Arguments:
            page (int): The page of the "My Stuff" projects that should be returned
            sort_by (str): The key the projects should be sorted based on. Possible values for this parameter are "" (then the projects are sorted based on last modified), "view_count", love_count", "remixers_count" (then the projects are sorted based on remix count) and "title" (then the projects are sorted based on title)
            descending (boolean): Determines if the element with the highest key value (the key is specified in the sort_by argument) should be returned first. Defaults to True.

        Returns:
            list<scratchattach.project.Project>: A list with the projects from the "My Stuff" page, each project is represented by a Project object.
        '''
        if descending:
            ascsort = ""
            descsort = sort_by
        else:
            ascsort = sort_by
            descsort = ""
        try:
            targets = requests.get(
                f"https://scratch.mit.edu/site-api/projects/{filter_arg}/?page={page}&ascsort={ascsort}&descsort={descsort}",
                headers = headers,
                cookies = self._cookies,
                timeout = 10,
            ).json()
            projects = []
            for target in targets:
                projects.append(project.Project(
                    id = target["pk"], _session=self, author_name=self._username,
                    comments_allowed=None, instructions=None, notes=None,
                    created=target["fields"]["datetime_created"],
                    last_modified=target["fields"]["datetime_modified"],
                    share_date=target["fields"]["datetime_shared"],
                    thumbnail_url="https:"+target["fields"]["thumbnail_url"],
                    favorites=target["fields"]["favorite_count"],
                    loves=target["fields"]["love_count"],
                    remixes=target["fields"]["remixers_count"],
                    views=target["fields"]["view_count"],
                    title=target["fields"]["title"],
                    comment_count=target["fields"]["commenters_count"]
                ))
            return projects
        except Exception:
            raise(exceptions.FetchError)

    def mystuff_studios(self, filter_arg="all", *, page=1, sort_by="", descending=True):
        if descending:
            ascsort = ""
            descsort = sort_by
        else:
            ascsort = sort_by
            descsort = ""
        try:
            targets = requests.get(
                f"https://scratch.mit.edu/site-api/galleries/{filter_arg}/?page={page}&ascsort={ascsort}&descsort={descsort}",
                headers = headers,
                cookies = self._cookies,
                timeout = 10,
            ).json()
            studios = []
            for target in targets:
                studios.append(studio.Studio(
                    id = target["pk"], _session=self,
                    title = target["fields"]["title"],
                    description = None,
                    host_id = target["fields"]["owner"]["pk"],
                    host_name = target["fields"]["owner"]["username"],
                    open_to_all = None, comments_allowed=None,
                    image_url = "https:"+target["fields"]["thumbnail_url"],
                    created = target["fields"]["datetime_created"],
                    modified = target["fields"]["datetime_modified"],
                    follower_count = None, manager_count = None,
                    curator_count = target["fields"]["curators_count"],
                    project_count = target["fields"]["projecters_count"]
                ))
            return studios
        except Exception:
            raise(exceptions.FetchError)


    def backpack(self,limit=20, offset=0):
        '''
        Lists the assets that are in the backpack of the user associated with the session.

        Returns:
            list<dict>: List that contains the backpack items as dicts
        '''
        data = commons.api_iterative(
            f"https://backpack.scratch.mit.edu/{self._username}",
            limit = limit, offset = offset, headers = self._headers
        )
        return commons.parse_object_list(data, backpack_asset.BackpackAsset, self)

    def delete_from_backpack(self, backpack_asset_id):
        '''
        Deletes an asset from the backpack.

        Args:
            backpack_asset_id: ID of the backpack asset that will be deleted
        '''
        return backpack_asset.BackpackAsset(id=backpack_asset_id, _session=self).delete()


    def become_scratcher_invite(self):
        """
        If you are a new Scratcher and have been invited for becoming a Scratcher, this API endpoint will provide more info on the invite.
        """
        return requests.get(f"https://api.scratch.mit.edu/users/{self.username}/invites", headers=self._headers, cookies=self._cookies).json()

    # --- Connect classes inheriting from BaseCloud ---

    def connect_cloud(self, project_id, *, CloudClass:Type[_base.BaseCloud]=cloud.ScratchCloud) -> Type[_base.BaseCloud]:
        """
        Connects to a cloud (by default Scratch's cloud) as logged in user.

        Args:
            project_id:
        
        Keyword arguments:
            CloudClass: The class that the returned object should be of. By default this class is scratchattach.cloud.ScratchCloud.

        Returns:
            Type[scratchattach._base.BaseCloud]: An object representing the cloud of a project. Can be of any class inheriting from BaseCloud.
        """
        return CloudClass(project_id=project_id, _session=self)

    def connect_scratch_cloud(self, project_id):
        """
        Returns:
            scratchattach.cloud.ScratchCloud: An object representing the Scratch cloud of a project.
        """
        return cloud.ScratchCloud(project_id=project_id, _session=self)

    def connect_tw_cloud(self, project_id, *, purpose="", contact="", cloud_host="wss://clouddata.turbowarp.org"):
        """
        Returns:
            scratchattach.cloud.TwCloud: An object representing the TurboWarp cloud of a project.
        """
        return cloud.TwCloud(project_id=project_id, purpose=purpose, contact=contact, cloud_host=cloud_host, _session=self)

    # --- Connect classes inheriting from BaseSiteComponent ---

    def _make_linked_object(self, identificator_name, identificator, Class, NotFoundException):
        """
        The Session class doesn't save the login in a ._session attribute, but IS the login ITSELF.

        Therefore the _make_linked_object method has to be adjusted
        to get it to work for in the Session class.

        Class must inherit from BaseSiteComponent
        """
        return commons._get_object(identificator_name, identificator, Class, NotFoundException, self)


    def connect_user(self, username) -> 'user.User':
        """
        Gets a user using this session, connects the session to the User object to allow authenticated actions

        Args:
            username (str): Username of the requested user

        Returns:
            scratchattach.user.User: An object that represents the requested user and allows you to perform actions on the user (like user.follow)
        """
        return self._make_linked_object("username", username, user.User, exceptions.UserNotFound)

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
        return self._make_linked_object("username", self.find_username_from_id(user_id), user.User, exceptions.UserNotFound)

    def connect_project(self, project_id):
        """
        Gets a project using this session, connects the session to the Project object to allow authenticated actions
sess
        Args:
            project_id (int): ID of the requested project

        Returns:
            scratchattach.project.Project: An object that represents the requested project and allows you to perform actions on the project (like project.love)
        """
        return self._make_linked_object("id", int(project_id), project.Project, exceptions.ProjectNotFound)

    def connect_studio(self, studio_id):
        """
        Gets a studio using this session, connects the session to the Studio object to allow authenticated actions

        Args:
            studio_id (int): ID of the requested studio

        Returns:
            scratchattach.studio.Studio: An object that represents the requested studio and allows you to perform actions on the studio (like studio.follow)
        """
        return self._make_linked_object("id", int(studio_id), studio.Studio, exceptions.StudioNotFound)

    def connect_classroom(self, class_id):
        """
        Gets a class using this session.

        Args:
            class_id (str): class id of the requested class

        Returns:
            scratchattach.classroom.Classroom: An object representing the requested classroom
        """
        return self._make_linked_object("id", int(class_id), classroom.Classroom, exceptions.ClassroomNotFound)

    def connect_classroom_from_token(self, class_token):
        """
        Gets a class using this session.

        Args:
            class_token (str): class token of the requested class

        Returns:
            scratchattach.classroom.Classroom: An object representing the requested classroom
        """
        return self._make_linked_object("classtoken", int(class_token), classroom.Classroom, exceptions.ClassroomNotFound)

    def connect_topic(self, topic_id):
        """
        Gets a forum topic using this session, connects the session to the ForumTopic object to allow authenticated actions
        Data is up-to-date. Data received from Scratch's RSS feed XML API.

        Args:
            topic_id (int): ID of the requested forum topic (can be found in the browser URL bar)

        Returns:
            scratchattach.forum.ForumTopic: An object that represents the requested forum topic
        """
        return self._make_linked_object("id", int(topic_id), forum.ForumTopic, exceptions.ForumContentNotFound)


    def connect_topic_list(self, category_id, *, page=1):

        """
        Gets the topics from a forum category. Data web-scraped from Scratch's forums UI.
        Data is up-to-date.

        Args:
            category_id (str): ID of the forum category

        Keyword Arguments:
            page (str): Page of the category topics that should be returned

        Returns:
            list<scratchattach.forum.ForumTopic>: A list containing the forum topics from the specified category
        """

        try:
            response = requests.get(f"https://scratch.mit.edu/discuss/{category_id}/?page={page}", headers=self._headers, cookies=self._cookies)
            soup = BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            raise exceptions.FetchError(str(e))

        try:
            category_name = soup.find('h4').find("span").get_text()
        except Exception as e:
            raise exceptions.BadRequest("Invalid category id")

        try:
            topics = soup.find_all('tr')
            topics.pop(0)
            return_topics = []

            for topic in topics:
                title_link = topic.find('a')
                title = title_link.text.strip()
                topic_id = title_link['href'].split('/')[-2]

                columns = topic.find_all('td')
                columns = [column.text for column in columns]
                if len(columns) == 1:
                    # This is a sticky topic -> Skip it
                    continue

                last_updated = columns[3].split(" ")[0] + " " + columns[3].split(" ")[1]

                return_topics.append(forum.ForumTopic(_session=self, id=int(topic_id), title=title, category_name=category_name, last_updated=last_updated, reply_count=int(columns[1]), view_count=int(columns[2])))
            return return_topics
        except Exception as e:
            raise exceptions.ScrapeError(str(e))

    # --- Connect classes inheriting from BaseEventHandler ---

    def connect_message_events(self, *, update_interval=2):
        # shortcut for connect_linked_user().message_events()
        return message_events.MessageEvents(user.User(username=self.username, _session=self), update_interval=update_interval)

    def connect_filterbot(self, *, log_deletions=True):
        return filterbot.Filterbot(user.User(username=self.username, _session=self), log_deletions=log_deletions)

# ------ #

def login_by_id(session_id, *, username=None, password=None, xtoken=None) -> Session:
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
    # Generate session_string (a scratchattach-specific authentication method)
    if password is not None:
        session_data = dict(session_id=session_id, username=username, password=password)
        session_string = base64.b64encode(json.dumps(session_data).encode())
    else:
        session_string = None
    _session = Session(id=session_id, username=username, session_string=session_string, xtoken=xtoken)
    try:
        status = _session.update()
    except Exception as e:
        status = False
        print(f"Key error at key "+str(e)+" when reading scratch.mit.edu/session API response")
    if status is not True:
        if _session.xtoken is None:
            if _session.username is None:
                print(f"Warning: Logged in by id, but couldn't fetch XToken. Make sure the provided session id is valid. Setting cloud variables can still work if you provide a `username='username'` keyword argument to the sa.login_by_id function")
            else:
                print(f"Warning: Logged in by id, but couldn't fetch XToken. Make sure the provided session id is valid.")
        else:
            print(f"Warning: Logged in by id, but couldn't fetch session info. This won't affect any other features.")
    return _session

def login(username, password, *, timeout=10) -> Session:
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
    return login_by_id(session_id, username=username, password=password)


def login_by_session_string(session_string):
    session_string = base64.b64decode(session_string).decode() # unobfuscate
    session_data = json.loads(session_string)
    try:
        assert session_data.get("session_id")
        return login_by_id(session_data["session_id"], username=session_data.get("username"), password=session_data.get("password"))
    except Exception:
        pass
    try:
        assert session_data.get("username") and session_data.get("password")
        return login(username=session_data["username"], password=session_data["password"])
    except Exception:
        pass
    raise ValueError("Couldn't log in.")
