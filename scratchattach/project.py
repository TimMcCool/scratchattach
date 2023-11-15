#----- Getting projects

import json
import requests
from . import user
from . import exceptions
from . import studio

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
    "x-csrftoken": "a",
    "x-requested-with": "XMLHttpRequest",
    "referer": "https://scratch.mit.edu",
}

class PartialProject:

    """
    Represents an unshared Scratch project that can't be accessed.
    """

    def __init__(self, **entries):

        self.shared = None
        self.project_token = None
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

    def remixes(self, *, limit=None, offset=0):
        """
        Returns:
            list<scratchattach.project.Project>: A list containing the remixes of the project, each project is represented by a Project object.
        """
        if limit is None:
            _projects = json.loads(requests.get(
                f"https://api.scratch.mit.edu/projects/{self.id}/remixes/?offset={offset}",
                headers = {
                    "x-csrftoken": "a",
                    "x-requested-with": "XMLHttpRequest",
                    "Cookie": "scratchcsrftoken=a;scratchlanguage=en;",
                    "referer": "https://scratch.mit.edu",
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
                }
            ).text)
        else:
            _projects = requests.get(
                f"https://api.scratch.mit.edu/projects/{self.id}/remixes/?limit={limit}&offset={offset}",
                headers = {
                    "x-csrftoken": "a",
                    "x-requested-with": "XMLHttpRequest",
                    "Cookie": "scratchcsrftoken=a;scratchlanguage=en;",
                    "referer": "https://scratch.mit.edu",
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
                }
            ).json()
        projects = []
        for project in _projects:
            projects.append(Project(
                author = project["author"]["username"],
                comments_allowed = project["comments_allowed"],
                description=project["description"],
                created = project["history"]["created"],
                last_modified = project["history"]["modified"],
                share_date = project["history"]["shared"],
                id = project["id"],
                thumbnail_url = project["image"],
                instructions = project["instructions"],
                remix_parent = project["remix"]["parent"],
                remix_root = project["remix"]["root"],
                favorites = project["stats"]["favorites"],
                loves = project["stats"]["loves"],
                remixes = project["stats"]["remixes"],
                views = project["stats"]["views"],
                title = project["title"],
                url = "https://scratch.mit.edu/projects/" + str(project["id"]),
                _session = self._session,
            ))
        return projects



class Project(PartialProject):

    '''
    Represents a Scratch project.

    Attributes:

    :.id: The project id

    :.url: The project url

    :.title:

    :.author: The username of the author

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
    '''

    def __str__(self):
        return self.title

    def update(self):
        """
        Updates the attributes of the Project object
        """
        if self._session is not None:
            project = requests.get(
                f"https://api.scratch.mit.edu/projects/{self.id}",
                headers = {
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36",
                    "x-token": self._session.xtoken,
                }
            )
            if "429" in str(project):
                return "429"
            if project.text == '{\n  "response": "Too many requests"\n}':
                return "429"
            project = project.json()
        else:
            project = requests.get(f"https://api.scratch.mit.edu/projects/{self.id}")
            if "429" in str(project):
                return "429"
            if project.text == '{\n  "response": "Too many requests"\n}':
                return "429"
            project = project.json()
        if "code" in list(project.keys()):
            return False
        else:
            return self._update_from_dict(project)

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
            self.update()
            response = requests.get(f"https://projects.scratch.mit.edu/{self.id}?token={self.project_token}")
            filename = filename.replace(".sb3", "")
            open(f"{dir}{filename}.sb3", 'wb').write(response.content)
        except Exception:
            raise(exceptions.FetchError("Method only works for projects created with Scratch 3"))

    def get_raw_json(self):
        """
        Method only works for project created with Scratch 3.

        Returns:
            dict: The project JSON
        """
        try:
            self.update()
            return requests.get(f"https://projects.scratch.mit.edu/{self.id}?token={self.project_token}").json()
        except Exception:
            raise(exceptions.FetchError("Method only works for projects created with Scratch 3"))

    def get_creator_agent(self):
        """
        Method only works for project created with Scratch 3.

        Returns:
            str: The user agent of the browser that this project was saved with.
        """
        try:
            self.update()
            return requests.get(f"https://projects.scratch.mit.edu/{self.id}?token={self.project_token}").json()["meta"]["agent"]
        except Exception:
            raise(exceptions.FetchError("Method only works for projects created with Scratch 3"))

    def _update_from_dict(self, project):
        try:
            self.id = int(project["id"])
        except KeyError:
            pass
        self.url = "https://scratch.mit.edu/projects/"+str(self.id)
        self.author = project["author"]["username"]
        self.comments_allowed = project["comments_allowed"]
        self.instructions = project["instructions"]
        self.notes=project["description"]
        self.created = project["history"]["created"]
        self.last_modified = project["history"]["modified"]
        self.share_date = project["history"]["shared"]
        self.thumbnail_url = project["image"]
        try:
            self.remix_parent = project["remix"]["parent"]
            self.remix_root = project["remix"]["root"]
        except Exception:
            self.remix_parent = None
            self.remix_root = None
        self.favorites = project["stats"]["favorites"]
        self.loves = project["stats"]["loves"]
        self.remix_count = project["stats"]["remixes"]
        self.views = project["stats"]["views"]
        self.title = project["title"]
        try:
            self.project_token = project["project_token"]
        except Exception:
            self.project_token = None
        return True

    def get_author(self):
        """
        Returns:
            scratchattach.user.User: An object representing the Scratch user who created this project.
        """
        try:
            return self._session.connect_user(self.author)
        except AttributeError:
            return user.get_user(self.author)


    def studios(self, *, limit=40, offset=0):
        """
        Returns:
            list<dict>: A list containing the studios this project is in, each studio is represented by a dict.
        """
        data = requests.get(f"https://api.scratch.mit.edu/users/{self.author}/projects/{self.id}/studios?limit={limit}&offset={offset}").json()
        return data
    
    def comments(self, *, limit=40, offset=0):
        """
        Returns the comments posted on the project (except for replies. To get replies use :meth:`scratchattach.project.Project.get_comment_replies`).

        Keyword Arguments:
            page: The page of the comments that should be returned.
            limit: Max. amount of returned comments.

        Returns:
            list<dict>: A list containing the requested comments as dicts.
        """

        comments = []
        while len(comments) < limit:
            r = requests.get(
                f"https://api.scratch.mit.edu/users/{self.author}/projects/{self.id}/comments/?limit={min(40, limit-len(comments))}&offset={offset}"
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
                f"https://api.scratch.mit.edu/users/{self.author}/projects/{self.id}/comments/{comment_id}/replies?limit={min(40, limit-len(comments))}&offset={offset}"
            ).json()
            if len(r) != 40:
                comments = comments + r
                break
            offset += 40
            comments = comments + r
        return comments

    def love(self):
        """
        Posts a love on the project. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_project`
        """
        if self._session is None:
            raise(exceptions.Unauthenticated)
            return
        r = requests.post(
            f"https://api.scratch.mit.edu/proxy/projects/{self.id}/loves/user/{self._session._username}",
            headers=self._headers,
            cookies=self._cookies,
        ).json()
        if r['userLove'] is False:
            self.love()

    def unlove(self):
        """
        Removes the love from this project. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_project`
        """
        if self._session is None:
            raise(exceptions.Unauthenticated)
            return
        r = requests.delete(
            f"https://api.scratch.mit.edu/proxy/projects/{self.id}/loves/user/{self._session._username}",
            headers = self._headers,
            cookies = self._cookies,
        ).json()
        if r['userLove'] is True:
            self.unlove()

    def favorite(self):
        """
        Posts a favorite on the project. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_project`
        """
        if self._session is None:
            raise(exceptions.Unauthenticated)
            return
        r = requests.post(
            f"https://api.scratch.mit.edu/proxy/projects/{self.id}/favorites/user/{self._session._username}",
            headers = self._headers,
            cookies = self._cookies,
        ).json()
        if r['userFavorite'] is False:
            self.favorite()

    def unfavorite(self):
        """
        Removes the favorite from this project. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_project`
        """
        if self._session is None:
            raise(exceptions.Unauthenticated)
            return
        r = requests.delete(
            f"https://api.scratch.mit.edu/proxy/projects/{self.id}/favorites/user/{self._session._username}",
            headers = self._headers,
            cookies = self._cookies,
        ).json()
        if r['userFavorite'] is True:
            self.unfavorite()


    def post_view(self):
        """
        Increases the project's view counter by 1.
        """
        requests.post(
            f"https://api.scratch.mit.edu/users/{self.author}/projects/{self.id}/views/",
            headers=headers,
        )

    def turn_off_commenting(self):
        """
        Disables commenting on the project. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_project`
        """
        if self._session is None:
            raise(exceptions.Unauthenticated)
            return
        if self._session._username != self.author:
            raise(exceptions.Unauthorized)
            return
        data = {
            "comments_allowed" : False
        }
        self._update_from_dict(requests.put(
            f"https://api.scratch.mit.edu/projects/{self.id}/",
            headers = self._json_headers,
            cookies = self._cookies,
            data = json.dumps(data)
        ).json())

    def turn_on_commenting(self):
        """
        Enables commenting on the project. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_project`
        """
        if self._session is None:
            raise(exceptions.Unauthenticated)
            return
        if self._session._username != self.author:
            raise(exceptions.Unauthorized)
            return
        data = {
            "comments_allowed" : True
        }
        self._update_from_dict(requests.put(
            f"https://api.scratch.mit.edu/projects/{self.id}/",
            headers = self._json_headers,
            cookies = self._cookies,
            data = json.dumps(data)
        ).json())



    def toggle_commenting(self):
        """
        Switches commenting on / off on the project (If comments are on, they will be turned off, else they will be turned on). You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_project`
        """
        if self._session is None:
            raise(exceptions.Unauthenticated)
            return
        if self._session._username != self.author:
            raise(exceptions.Unauthorized)
            return
        data = {
            "comments_allowed" : not self.comments_allowed
        }
        self._update_from_dict(requests.put(
            f"https://api.scratch.mit.edu/projects/{self.id}/",
            headers = self._json_headers,
            cookies = self._cookies,
            data = json.dumps(data)
        ).json())

    def share(self):
        """
        Shares the project. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_project`
        """
        if self._session is None:
            raise(exceptions.Unauthenticated)
            return
        if self._session._username != self.author:
            raise(exceptions.Unauthorized)
            return
        if self.shared is not True:
            requests.put(f"https://api.scratch.mit.edu/proxy/projects/{self.id}/share/",
                headers = self._json_headers,
                cookies = self._cookies,
            )

    def unshare(self):
        """
        Unshares the project. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_project`
        """
        if self._session is None:
            raise(exceptions.Unauthenticated)
            return
        if self._session._username != self.author:
            raise(exceptions.Unauthorized)
            return
        if self.shared is not False:
            requests.put(f"https://api.scratch.mit.edu/proxy/projects/{self.id}/unshare/",
                headers = self._json_headers,
                cookies = self._cookies,
            )

    def set_thumbnail(self, *, file):
        """
        You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_project`
        """
        if self._session is None:
            raise(exceptions.Unauthenticated)
            return
        if self._session._username != self.author:
            raise(exceptions.Unauthorized)
            return
        with open(file, "rb") as f:
            thumbnail = f.read()
        requests.post(
            f"https://scratch.mit.edu/internalapi/project/thumbnail/{self.id}/set/",
            data = thumbnail,
            headers = self._headers,
            cookies = self._cookies,
        )

    def delete_comment(self, *, comment_id):
        """
        Deletes a comment. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_project`

        Args:
            comment_id: The id of the comment that should be deleted
        """
        if self._session is None:
            raise(exceptions.Unauthenticated)
            return
        if self._session._username != self.author:
            raise(exceptions.Unauthorized)
            return
        return requests.delete(
            f"https://api.scratch.mit.edu/proxy/comments/project/{self.id}/comment/{comment_id}/",
            headers = self._headers,
            cookies = self._cookies,
        ).headers

    def report_comment(self, *, comment_id):
        """
        Reports a comment to the Scratch team. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_project`

        Args:
            comment_id: The id of the comment that should be reported
        """
        if self._session is None:
            raise(exceptions.Unauthenticated)
            return
        return requests.delete(
            f"https://api.scratch.mit.edu/proxy/comments/project/{self.id}/comment/{comment_id}/report",
            headers = self._headers,
            cookies = self._cookies,
        )

    def post_comment(self, content, *, parent_id="", commentee_id=""):
        """
        Posts a comment on the project. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_project`

        Args:
            content: Content of the comment that should be posted

        Keyword Arguments:
            parent_id: ID of the comment you want to reply to. If you don't want to mention a user, don't put the argument.
            commentee_id: ID of the user that will be mentioned in your comment and will receive a message about your comment. If you don't want to mention a user, don't put the argument.
        """
        if self._session is None:
            raise(exceptions.Unauthenticated)
            return
        data = {
            "commentee_id": commentee_id,
            "content": str(content),
            "parent_id": parent_id,
        }
        headers = self._json_headers
        headers["referer"] = "https://scratch.mit.edu/projects/" + str(self.id) + "/"
        return json.loads(requests.post(
            f"https://api.scratch.mit.edu/proxy/comments/project/{self.id}/",
            headers = headers,
            cookies = self._cookies,
            data=json.dumps(data),
        ).text)


    def reply_comment(self, content, *, parent_id, commentee_id=""):
        """
        Posts a reply to a comment on the project. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_project`

        Args:
            content: Content of the comment that should be posted

        Keyword Arguments:
            parent_id: ID of the comment you want to reply to
            commentee_id: ID of the user that will be mentioned in your comment and will receive a message about your comment. If you don't want to mention a user, don't put the argument.
        """
        return self.post_comment(content, parent_id=parent_id, commentee_id=commentee_id)

    def set_json(self, json_data):
        """
        Sets the project json. You can use this to upload projects to the Scratch website.

        Args:
            json_data (dict or JSON): The new project JSON as encoded JSON object or as dict
        """

        if not isinstance(json_data, dict):
            json_data = json.loads(json_data)

        if self._session is None:
            raise(exceptions.Unauthenticated)
            return
        if self._session._username != self.author:
            raise(exceptions.Unauthorized("You must be the project owner to do this."))
            return

        r = requests.put(
            f"https://projects.scratch.mit.edu/{self.id}",
            headers = self._headers,
            cookies = self._cookies,
            json=json_data,
        ).json()

    def set_title(self, text):
        """
        Changes the projects title. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_project`
        """
        if self._session is None:
            raise(exceptions.Unauthenticated)
            return
        if self._session._username != self.author:
            raise(exceptions.Unauthorized("You must be the project owner to do this."))
            return
        r = requests.put(f"https://api.scratch.mit.edu/projects/{self.id}",
            headers = self._headers,
            cookies = self._cookies,
            data=json.dumps({"title":text})).json()
        return self._update_from_dict(r)

    def set_instructions(self, text):
        """
        Changes the projects instructions. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_project`
        """
        if self._session is None:
            raise(exceptions.Unauthenticated)
            return
        if self._session._username != self.author:
            raise(exceptions.Unauthorized("You must be the project owner to do this."))
            return
        r = requests.put(f"https://api.scratch.mit.edu/projects/{self.id}",
            headers = self._headers,
            cookies = self._cookies,
            data=json.dumps({"instructions":text})).json()
        return self._update_from_dict(r)

    def set_notes(self, text):
        """
        Changes the projects notes and credits. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_project`
        """
        if self._session is None:
            raise(exceptions.Unauthenticated)
            return
        if self._session._username != self.author:
            raise(exceptions.Unauthorized("You must be the project owner to do this."))
            return
        r = requests.put(f"https://api.scratch.mit.edu/projects/{self.id}",
            headers = self._headers,
            cookies = self._cookies,
            data=json.dumps({"description":text})).json()
        return self._update_from_dict(r)

    def ranks(self):
        """
        Gets information about the project's ranks. Fetched from ScratchDB.

        Returns:
            dict: A dict containing the project's ranks. If the ranks aren't available, all values will be -1.
        """
        return requests.get(f"https://scratchdb.lefty.one/v3/project/info/{self.id}").json()["statistics"]["ranks"]

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
            return requests.get(f"https://jeffalo.net/api/nfe/?project={self.id}").json()["status"]
        except Exception:
            raise(exceptions.FetchError)



# ------ #

def get_project(project_id):
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
    try:
        project = Project(id=int(project_id))
        u = project.update()
        if u == "429":
            raise(exceptions.Response429("Your network is blocked or rate-limited by Scratch.\nIf you're using an online IDE like replit.com, try running the code on your computer."))
        if not u:
            project = PartialProject(id=int(project_id), author=None, title=None, shared=False, instructions=None, notes=None, loves=None, views=None, favorites=None)
        return project
    except KeyError:
        return None
    except Exception as e:
        raise(e)


def explore_projects(*, query="*", mode="trending", language="en", limit=40, offset=0):
    '''
    Gets projects from the explore page without logging in.

    Keyword arguments:
        query (str): Specifies the tag of the explore page. To get the projects from the "All" tag, set this argument to "*".
        mode (str): Has to be one of these values: "trending", "popular" or "recent". Defaults to "trending".
        language (str): A language abbreviation, defaults to "en". (Depending on the language used on the Scratch website, Scratch displays you different explore pages.)
        limit (int): Max. amount of returned projects.
        offset (int): Offset of the first returned project.

    Returns:
        list<scratchattach.project.Project>: List that contains the explore page projects

    Warning:
        Any methods that require authentication (like project.love) will not work on the returned objects.

        If you want to use these methods, get the explore page projects with :meth:`scratchattach.session.Session.search_projects` instead.
    '''

    r = requests.get(f"https://api.scratch.mit.edu/explore/projects?limit={limit}&offset={offset}&language={language}&mode={mode}&q={query}").json()
    projects = []

    for project in r:
        p = Project()
        p._update_from_dict(project)
        projects.append(p)
    return projects

def search_projects(*, query="", mode="trending", language="en", limit=40, offset=0):
    '''
    Uses the Scratch search to search projects without logging in.

    Keyword arguments:
        query (str): The query that will be searched.
        mode (str): Has to be one of these values: "trending", "popular" or "recent". Defaults to "trending".
        language (str): A language abbreviation, defaults to "en". (Depending on the language used on the Scratch website, Scratch displays you different results.)
        limit (int): Max. amount of returned projects.
        offset (int): Offset of the first returned project.

    Returns:
        list<scratchattach.project.Project>: List that contains the search results

    Warning:
        Any methods that require authentication (like project.love) will not work on the returned objects.

        If you want to use these methods, perform the search with :meth:`scratchattach.session.Session.search_projects` instead.
    '''
    r = requests.get(f"https://api.scratch.mit.edu/search/projects?limit={limit}&offset={offset}&language={language}&mode={mode}&q={query}").json()
    projects = []

    for project in r:
        p = Project()
        p._update_from_dict(project)
        projects.append(p)
    return projects
