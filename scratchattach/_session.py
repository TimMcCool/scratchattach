#----- Connecting to a Scratch account

import json
import re
import requests

from . import _user
from . import _cloud
from . import _project
from . import _exceptions
from . import _studio
from . import _forum

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
    "x-csrftoken": "a",
    "x-requested-with": "XMLHttpRequest",
    "referer": "https://scratch.mit.edu",
}

class Session():

    def __init__(self, session_id, *, username=None):

        self.session_id = str(session_id)
        self._username = username
        self._headers = headers
        self._cookies = {
            "scratchsessionsid" : self.session_id,
            "scratchcsrftoken" : "a",
            "scratchlanguage" : "en",
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        self._get_xtoken()
        try:
            self._headers.pop("Cookie")
        except Exception: pass

    def _get_csrftoken(self):
        r = requests.get("https://scratch.mit.edu/csrf_token/").headers
        print(r)
        csrftoken = r["Set-Cookie"].split("scratchcsrftoken=")[1].split(";")[0]
        self._headers["x-csrftoken"] = csrftoken
        self._cookies["scratchcsrftoken"] = csrftoken

    def _get_xtoken(self):

        # this will fetch the account token
        try:
            response = json.loads(requests.post(
                "https://scratch.mit.edu/session",
                headers = {
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
                    "x-csrftoken": "a",
                    "x-requested-with": "XMLHttpRequest",
                    "referer": "https://scratch.mit.edu",
                },
                cookies = {
                    "scratchsessionsid" : self.session_id,
                    "scratchcsrftoken" : "a",
                    "scratchlanguage" : "en"
                }
            ).text)

            self.xtoken = response['user']['token']
            self._headers["X-Token"] = self.xtoken
            self.email = response["user"]["email"]
            self.new_scratcher = response["permissions"]["new_scratcher"]
            self.mute_status = response["permissions"]["mute_status"]
            self._username = response["user"]["username"]
            self.banned = response["user"]["banned"]
            if self.banned:
                print("Warning: The account you logged in to is BANNED. Some features may not work properly.")

        except Exception:
            if self._username is None:
                print("Warning: Logged in, but couldn't fetch XToken.\nSome features (including cloud variables) will not work properly. To get cloud variables to work, provide a username argument: Session('session_id', username='username')\nIf you're using an online IDE (like replit.com) Scratch possibly banned its IP adress.")
            else:
                print("Warning: Logged in, but couldn't fetch XToken. Cloud variables will still work, but other features may not work properly.\nIf you're using an online IDE (like replit.com) Scratch possibly banned its IP adress.")
            self.xtoken = ""

    def get_linked_user(self):

        #this will fetch the user who is associated to the session
        if not "_user" in self.__dict__:
            self._user = self.connect_user(self._username)
        return self._user

    def mystuff_projects(self, ordering, *, page=1, sort_by=""):
        try:
            targets = requests.get(
                f"https://scratch.mit.edu/site-api/projects/{ordering}/?page={page}&ascsort=&descsort={sort_by}",
                headers = headers,
                cookies = self._cookies,
            ).json()
            projects = []
            for target in targets:
                projects.append(
                    dict(
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
            raise(_exceptions.FetchError)

    def get_mystuff_projects(self, ordering, *, page=1, sort_by=""):
        return self.mystuff_projects(ordering, page=page, sort_by=sort_by)

    def messages(self, *, limit=40, offset=0):

        return requests.get(
            f"https://api.scratch.mit.edu/users/{self._username}/messages?limit={limit}&offset={offset}",
            headers = self._headers,
            cookies = self._cookies,
        ).json()

    def clear_messages(self):

        return requests.post(
            "https://scratch.mit.edu/site-api/messages/messages-clear/",
            headers = self._headers,
            cookies = self._cookies,
        ).text

    def message_count(self):

        return json.loads(requests.get(f"https://api.scratch.mit.edu/users/{self._username}/messages/count/", headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.3c6 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',}).text)["count"]

    def get_feed(self, *, limit=20, offset=0):
        return requests.get(
            f"https://api.scratch.mit.edu/users/{self._username}/following/users/activity?limit={limit}&offset={offset}",
            headers = self._headers,
            cookies = self._cookies
        ).json()

    def create_project(self):

        try:

            return self.connect_project(requests.post(
                "https://projects.scratch.mit.edu/",
                headers = headers,
                cookies = self._cookies
            ).json()["content-name"])
        except Exception:
            raise(_exceptions.FetchError)

    '''
    def created_by_followed_users(self, *, limit=40, offset=0):
        r = requests.get(
            f"https://api.scratch.mit.edu/users/{self._username}/following/users/projects?limit={limit}&offset={offset}",
            headers = self._headers,
            cookies = self._cookies
        ).json()
        projects = []

        for project in r:
            p = _project.Project()
            p._update_from_dict(project)
            projects.append(p)
        return projects

    def added_to_followed_studios(self, *, limit=40, offset=0):
        r = requests.get(
            f"https://api.scratch.mit.edu/users/{self._username}/following/studios/projects?limit={limit}&offset={offset}",
            headers = self._headers,
            cookies = self._cookies
        ).json()
        projects = []

        for project in r:
            p = _project.Project()
            p._update_from_dict(project)
            projects.append(p)
        return projects
    '''

    def loved_by_followed_users(self, *, limit=40, offset=0):
        r = requests.get(
            f"https://api.scratch.mit.edu/users/{self._username}/following/users/loves?limit={limit}&offset={offset}",
            headers = self._headers,
            cookies = self._cookies
        ).json()
        projects = []

        for project in r:
            p = _project.Project(_session = self)
            p._update_from_dict(project)
            projects.append(p)
        return projects

    def search_projects(self, *, query="", mode="trending", language="en", limit=40, offset=0):
        r = requests.get(f"https://api.scratch.mit.edu/search/projects?limit={limit}&offset={offset}&language={language}&mode={mode}&q={query}").json()
        projects = []

        for project in r:
            p = _project.Project(_session = self)
            p._update_from_dict(project)
            projects.append(p)
        return projects

    def explore_projects(self, *, query="", mode="trending", language="en", limit=40, offset=0):
        r = requests.get(f"https://api.scratch.mit.edu/explore/projects?limit={limit}&offset={offset}&language={language}&mode={mode}&q={query}").json()
        projects = []

        for project in r:
            p = _project.Project(_session = self)
            p._update_from_dict(project)
            projects.append(p)
        return projects


    def backpack(self,limit=20, offset=0):
        return requests.get(
            f"https://backpack.scratch.mit.edu/{self._username}?limit={limit}&offset={offset}",
            headers = self._headers,
        ).json()

    def delete_from_backpack(self, asset_id):
        return requests.delete(
            f"https://backpack.scratch.mit.edu/{self._username}/{asset_id}",
            headers = self._headers,
        ).json()

    def connect_cloud(self, project_id_arg=None, *, project_id=None):
        if project_id is None:
            project_id = project_id_arg
        if project_id is None:
            return None

        return _cloud.CloudConnection(username = self._username, session_id = self.session_id, project_id = int(project_id))


    def connect_user(self, username):
        try:
            user = _user.User(username=username, _session=self)
            if user.update() == "429":
                raise(_exceptions.Response429("Your network is blocked or rate-limited by Scratch.\nIf you're using an online IDE like replit.com, try running the code on your computer."))
            return user
        except KeyError:
            return None
        except Exception as e:
            raise(e)

    def connect_project(self, project_id):
        try:
            project = _project.Project(id=int(project_id), _session=self)
            u = project.update()
            if u == "429":
                raise(_exceptions.Response429("Your network is blocked or rate-limited by Scratch.\nIf you're using an online IDE like replit.com, try running the code on your computer."))
            if not u:
                project = _project.PartialProject(id=int(project_id))
            return project
        except KeyError:
            return None
        except Exception as e:
            raise(e)

    def connect_studio(self, studio_id):
        try:
            studio = _studio.Studio(id=int(studio_id), _session=self)
            if studio.update() == "429":
                raise(_exceptions.Response429("Your network is blocked or rate-limited by Scratch.\nIf you're using an online IDE like replit.com, try running the code on your computer."))
            return studio
        except KeyError:
            return None
        except Exception as e:
            raise(e)

    def connect_topic(self, topic_id):

        """
        Connects a forum topic
        """

        try:
            topic = _forum.ForumTopic(id=int(topic_id), _session=self)
            topic.update()
            return topic
        except KeyError:
            return None

    def connect_topic_list(self, category_name, *, page=0, include_deleted=False):
        category_name.replace(" ", "%20")
        if include_deleted:
            filter = 0
        else:
            filter = 1
        try:
            data = requests.get(f"https://scratchdb.lefty.one/v3/forum/category/topics/{category_name}/{page}?detail=1&filter={filter}").json()
            return_data = []
            for topic in data:
                t = _forum.ForumTopic(id = topic["id"], _session=self)
                t._update_from_dict(topic)
                return_data.append(t)
            return return_data
        except Exception:
            return None

    def connect_post(self, post_id):

        """
        Gets a forum post
        """

        try:
            post = _forum.ForumPost(id=int(post_id), _session=self)
            post.update()
            return post
        except KeyError:
            return None

    def search_posts(self, *, query, order="newest", page=0):
        try:
            data = requests.get(f"https://scratchdb.lefty.one/v3/forum/search?q={query}&o={order}&page={page}").json()["posts"]
            return_data = []
            for o in data:
                a = _forum.ForumPost(id = o["id"], _session = self._session)
                a._update_from_dict(o)
                return_data.append(a)
            return return_data
        except Exception:
            return []

# ------ #

def login(username, password):
    data = json.dumps({"username": username, "password": password})
    _headers = headers
    _headers["Cookie"] = "scratchcsrftoken=a;scratchlanguage=en;"
    request = requests.post(
        "https://scratch.mit.edu/login/", data=data, headers=_headers
    )
    try:
        session_id = str(re.search('"(.*)"', request.headers["Set-Cookie"]).group())
    except Exception:
        raise _exceptions.LoginFailure("Either the provided authentication data is wrong or your network is banned from Scratch.\n\nIf you're using an online IDE (like replit.com) Scratch possibly banned its IP adress. In this case, try logging in with your session id: https://github.com/TimMcCool/scratchattach#logging-in--scratch3session")
    session = Session(session_id, username=username)
    return session


def get_news(*, limit=10, offset=0):
    return requests.get(f"https://api.scratch.mit.edu/news?limit={limit}&offset={offset}").json()

def featured_projects():
    return requests.get("https://api.scratch.mit.edu/proxy/featured").json()["community_featured_projects"]

def featured_studios():
    return requests.get("https://api.scratch.mit.edu/proxy/featured").json()["community_featured_studios"]

def top_loved():
    return requests.get("https://api.scratch.mit.edu/proxy/featured").json()["community_most_loved_projects"]

def top_remixed():
    return requests.get("https://api.scratch.mit.edu/proxy/featured").json()["community_most_remixed_projects"]

def newest_projects():
    return requests.get("https://api.scratch.mit.edu/proxy/featured").json()["community_newest_projects"]

def curated_projects():
    return requests.get("https://api.scratch.mit.edu/proxy/featured").json()["curator_top_projects"]

def design_studio_projects():
    return requests.get("https://api.scratch.mit.edu/proxy/featured").json()["scratch_design_studio"]

def search_projects(*, query="", mode="trending", language="en", limit=40, offset=0):
        r = requests.get(f"https://api.scratch.mit.edu/search/projects?limit={limit}&offset={offset}&language={language}&mode={mode}&q={query}").json()
        projects = []

        for project in r:
            p = _project.Project()
            p._update_from_dict(project)
            projects.append(p)
        return projects

def search_studios(*, query="", mode="trending", language="en", limit=40, offset=0):
    return requests.get(f"https://api.scratch.mit.edu/search/studios?limit={limit}&offset={offset}&language={language}&mode={mode}&q={query}").json()

def explore_projects(*, query="", mode="trending", language="en", limit=40, offset=0):
        r = requests.get(f"https://api.scratch.mit.edu/explore/projects?limit={limit}&offset={offset}&language={language}&mode={mode}&q={query}").json()
        projects = []

        for project in r:
            p = _project.Project()
            p._update_from_dict(project)
            projects.append(p)
        return projects

def explore_studios(*, query="", mode="trending", language="en", limit=40, offset=0):
    return requests.get(f"https://api.scratch.mit.edu/explore/studios?limit={limit}&offset={offset}&language={language}&mode={mode}&q={query}").json()

def search_comments(*, query=""):
    print("WARNING: scratchattach.Session.search_comments does not work anymore")
    return {}
    #return requests.get(f"https://sd.sly-little-fox.ru/api/v1/search?q={query}").json()

def search_posts(*, query, order="newest", page=0):
    try:
        data = requests.get(f"https://scratchdb.lefty.one/v3/forum/search?q={query}&o={order}&page={page}").json()["posts"]
        return_data = []
        for o in data:
            a = _forum.ForumPost(id = o["id"])
            a._update_from_dict(o)
            return_data.append(a)
        return return_data
    except Exception:
        return []

def total_site_stats():
    data = requests.get("https://scratch.mit.edu/statistics/data/daily/").json()
    data.pop("_TS")
    return data

def monthly_site_traffic():
    data = requests.get("https://scratch.mit.edu/statistics/data/monthly-ga/").json()
    data.pop("_TS")
    return data

def country_counts():
    return requests.get("https://scratch.mit.edu/statistics/data/monthly/").json()["country_distribution"]

def age_distribution():
    data = requests.get("https://scratch.mit.edu/statistics/data/monthly/").json()["age_distribution_data"][0]["values"]
    return_data = {}
    for value in data:
        return_data[value["x"]] = value["y"]
    return return_data

def get_health():
    return requests.get("https://api.scratch.mit.edu/health").json()

def get_csrf_token():
    return requests.get(
        "https://scratch.mit.edu/csrf_token/"
    ).headers["set-cookie"].split(";")[3][len(" Path=/, scratchcsrftoken="):]
