#----- Getting users

import json
import requests
from . import _project
from . import _exceptions
from . import _forum
from bs4 import BeautifulSoup

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
    "x-csrftoken": "a",
    "x-requested-with": "XMLHttpRequest",
    "referer": "https://scratch.mit.edu",
}

class User:

    def __init__(self, **entries):
        self.__dict__.update(entries)

        if "bio" in self.__dict__:
            self.about_me = self.bio
        if "status" in self.__dict__:
            self.wiwo = self.status

        if "name" in self.__dict__.keys():
            self.username = self.name
        if "username" in self.__dict__.keys():
            self.name = self.username

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

    def __str__(self):
        return str(self.username)

    def update(self):
        r = requests.get(f"https://api.scratch.mit.edu/users/{self.username}/")
        if "429" in str(r):
            return "429"
        if r.text == '{\n  "response": "Too many requests"\n}':
            return "429"
        response = json.loads(r.text)
        self._update_from_dict(response)

    def _update_from_dict(self, response):
        try:

            self.id = response["id"]

        except Exception:
            raise(_exceptions.UserNotFound)
        self.scratchteam = response["scratchteam"]
        self.join_date = response["history"]["joined"]
        self.about_me = response["profile"]["bio"]
        self.wiwo = response["profile"]["status"]
        self.country = response["profile"]["country"]
        self.icon_url = response["profile"]["images"]["90x90"]

    def message_count(self):

        return json.loads(requests.get(f"https://api.scratch.mit.edu/users/{self.username}/messages/count/", headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.3c6 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',}).text)["count"]

    def featured_data(self):
        # featured data
        try:
            response = json.loads(requests.get(f"https://scratch.mit.edu/site-api/users/all/{self.username}/").text)
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

    def follower_count(self):
        # follower count
        text = requests.get(
            f"https://scratch.mit.edu/users/{self.username}/followers/",
            headers = {
                "x-csrftoken": "a",
                "x-requested-with": "XMLHttpRequest",
                "Cookie": "scratchcsrftoken=a;scratchlanguage=en;",
                "referer": "https://scratch.mit.edu",
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
            }
        ).text
        text = text.split("Followers (")[1]
        text = text.split(")")[0]
        return int(text)

    def following_count(self):
        # following count
        text = requests.get(
            f"https://scratch.mit.edu/users/{self.username}/following/",
            headers = {
                "x-csrftoken": "a",
                "x-requested-with": "XMLHttpRequest",
                "Cookie": "scratchcsrftoken=a;scratchlanguage=en;",
                "referer": "https://scratch.mit.edu",
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
            }
        ).text
        text = text.split("Following (")[1]
        text = text.split(")")[0]
        return int(text)

    def followers(self, *, limit=40, offset=0):

        if limit>40:
            limit=40
        followers = []
        response = requests.get(
            f"https://api.scratch.mit.edu/users/{self.username}/followers/?limit={limit}&offset={offset}").json()
        for follower in response:
            try:
                followers.append(User(
                    id = follower["id"],
                    name = follower["username"],
                    scratchteam = follower["scratchteam"],
                    join_date = follower["history"]["joined"],
                    icon_url = follower["profile"]["images"]["90x90"],
                    status = follower["profile"]["status"],
                    bio = follower["profile"]["bio"],
                    country = follower["profile"]["country"]
                ))
            except Exception:
                print("Failed to parse ", follower)
        return followers

    def following(self, *, limit=40, offset=0):
        if limit>40:
            limit=40
        followers = []
        response = requests.get(
            f"https://api.scratch.mit.edu/users/{self.username}/following/?limit={limit}&offset={offset}").json()
        for follower in response:
            try:
                followers.append(User(
                    id = follower["id"],
                    name = follower["username"],
                    scratchteam = follower["scratchteam"],
                    join_date = follower["history"]["joined"],
                    icon_url = follower["profile"]["images"]["90x90"],
                    status = follower["profile"]["status"],
                    bio = follower["profile"]["bio"],
                    country = follower["profile"]["country"]
                ))
            except Exception:
                print("Failed to parse ", follower)
        return followers

    '''def get_comments(self, *, page=1):
        response = requests.get(f"https://scratch.mit.edu/site-api/comments/user/{self.z}/?page=1")'''

    def is_following(self, user):
        return requests.get(f"https://following-check.1tim.repl.co/api/{self.username}/?following={user}").json()["following"]

    def is_followed_by(self, user):
        return requests.get(f"https://following-check.1tim.repl.co/api/{user}/?following={self.username}").json()["following"]

    def project_count(self):
        text = requests.get(
            f"https://scratch.mit.edu/users/{self.username}/projects/",
            headers = {
                "x-csrftoken": "a",
                "x-requested-with": "XMLHttpRequest",
                "Cookie": "scratchcsrftoken=a;scratchlanguage=en;",
                "referer": "https://scratch.mit.edu",
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
            }
        ).text
        text = text.split("Shared Projects (")[1]
        text = text.split(")")[0]
        return int(text)

    def project_count(self):
        text = requests.get(
            f"https://scratch.mit.edu/users/{self.username}/projects/",
            headers = {
                "x-csrftoken": "a",
                "x-requested-with": "XMLHttpRequest",
                "Cookie": "scratchcsrftoken=a;scratchlanguage=en;",
                "referer": "https://scratch.mit.edu",
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
            }
        ).text
        text = text.split("Shared Projects (")[1]
        text = text.split(")")[0]
        return int(text)

    def studio_count(self):
        text = requests.get(
            f"https://scratch.mit.edu/users/{self.username}/studios/",
            headers = {
                "x-csrftoken": "a",
                "x-requested-with": "XMLHttpRequest",
                "Cookie": "scratchcsrftoken=a;scratchlanguage=en;",
                "referer": "https://scratch.mit.edu",
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
            }
        ).text
        text = text.split("Studios I Curate (")[1]
        text = text.split(")")[0]
        return int(text)

    def studios_following_count(self):
        text = requests.get(
            f"https://scratch.mit.edu/users/{self.username}/studios/",
            headers = {
                "x-csrftoken": "a",
                "x-requested-with": "XMLHttpRequest",
                "Cookie": "scratchcsrftoken=a;scratchlanguage=en;",
                "referer": "https://scratch.mit.edu",
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
            }
        ).text
        text = text.split("Studios I Follow (")[1]
        text = text.split(")")[0]
        return int(text)

    def studios(self, *, limit=40, offset=0):
        return requests.get(f"https://api.scratch.mit.edu/users/{self.username}/studios/curate?limit={limit}&offset={offset}").json()

    def projects(self, *, limit=None, offset=0):
        if limit is None:
            _projects = json.loads(requests.get(
                f"https://api.scratch.mit.edu/users/{self.username}/projects/?offset={offset}",
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
                f"https://api.scratch.mit.edu/users/{self.username}/projects/?limit={limit}&offset={offset}",
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
            projects.append(_project.Project(
                _session = self._session,
                author = self.username,
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
                url = "https://scratch.mit.edu/projects/"+str(project["id"])
            ))
        return projects

    def favorites(self, *, limit=None, offset=0):
        if limit is None:
            _projects = json.loads(requests.get(
                f"https://api.scratch.mit.edu/users/{self.username}/favorites/?offset={offset}",
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
                f"https://api.scratch.mit.edu/users/{self.username}/favorites/?limit={limit}&offset={offset}",
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
            projects.append(_project.Project(
                _session = self._session,
                author = self.username,
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
                url = "https://scratch.mit.edu/projects/"+str(project["id"])
            ))
        return projects

    def favorites_count(self):
        text = requests.get(
            f"https://scratch.mit.edu/users/{self.username}/favorites/",
            headers = {
                "x-csrftoken": "a",
                "x-requested-with": "XMLHttpRequest",
                "Cookie": "scratchcsrftoken=a;scratchlanguage=en;",
                "referer": "https://scratch.mit.edu",
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
            }
        ).text
        text = text.split("Favorites (")[1]
        text = text.split(")")[0]
        return int(text)

    def toggle_commenting(self):
        requests.post(f"https://scratch.mit.edu/site-api/comments/user/{self.username}/toggle-comments/",
            headers = headers,
            cookies = self._cookies
        )

    def viewed_projects(self, limit=24, offset=0):
        try:
            _projects = requests.get(
                f"https://api.scratch.mit.edu/users/{self.username}/projects/recentlyviewed?limit={limit}&offset={offset}",
                headers = self._headers
            ).json()
            projects = []
            for project in _projects:
                projects.append(_project.Project(
                    _session = self._session,
                    author = self.username,
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
                    url = "https://scratch.mit.edu/projects/"+str(project["id"])
                ))
            return projects
        except Exception:
            raise(_exceptions.Unauthorized)


    def set_bio(self, text):
        requests.put(
            f"https://scratch.mit.edu/site-api/users/all/{self.username}/",
            headers = self._json_headers,
            cookies = self._cookies,
            data = json.dumps(dict(
                comments_allowed = True,
                id = self.username,
                bio = text,
                thumbnail_url = self.icon_url,
                userId = self.id,
                username = self.username
            ))
        )

    def set_wiwo(self, text):
        requests.put(
            f"https://scratch.mit.edu/site-api/users/all/{self.username}/",
            headers = self._json_headers,
            cookies = self._cookies,
            data = json.dumps(dict(
                comments_allowed = True,
                id = self.username,
                status = text,
                thumbnail_url = self.icon_url,
                userId = self.id,
                username = self.username
            ))
        )

    def set_featured(self, project_id, *, label=""):
        requests.put(
            f"https://scratch.mit.edu/site-api/users/all/{self.username}/",
            headers = self._json_headers,
            cookies = self._cookies,
            data = json.dumps({"featured_project":int(project_id),"featured_project_label":label})
        )


    def post_comment(self, content, *, parent_id="", commentee_id=""):
        data = {
            "commentee_id": commentee_id,
            "content": content,
            "parent_id": parent_id,
        }
        return requests.post(
            f"https://scratch.mit.edu/site-api/comments/user/{self.username}/add/",
            headers = headers,
            cookies = self._cookies,
            data=json.dumps(data),
        )

    def reply_comment(self, content, *, parent_id, commentee_id=""):
        return self.post_comment(content, parent_id=parent_id, commentee_id=commentee_id)

    def activity_html(self, *, limit=1000):
        return requests.get(f"https://scratch.mit.edu/messages/ajax/user-activity/?user={self.username}&max={limit}").text


    def follow(self):
        requests.put(
            f"https://scratch.mit.edu/site-api/users/followers/{self.username}/add/?usernames={self._session._username}",
            headers = headers,
            cookies = self._cookies,
        )

    def unfollow(self):
        requests.put(
            f"https://scratch.mit.edu/site-api/users/followers/{self.username}/remove/?usernames={self._session._username}",
            headers = headers,
            cookies = self._cookies,
        )

    def delete_comment(self, *, comment_id):
        return requests.post(
            f"https://scratch.mit.edu/site-api/comments/user/{self.username}/del/",
            headers = headers,
            cookies = self._cookies,
            data = json.dumps({"id":str(comment_id)})
        )

    def report_comment(self, *, comment_id):
        return requests.post(
            f"https://scratch.mit.edu/site-api/comments/user/{self.username}/rep/",
            headers = headers,
            cookies = self._cookies,
            data = json.dumps({"id":str(comment_id)})
        )

    def _get_comments(self, URL):
        DATA = []

        page_contents = requests.get(URL).content

        soup = BeautifulSoup(page_contents, "html.parser")

        comments = soup.find_all("li", {"class": "top-level-reply"})

        if len(comments) == 0:
            return None

        for comment in comments:
            comment_id = comment.find("div", {"class": "comment"})['data-comment-id']
            user = comment.find("a", {"id": "comment-user"})['data-comment-user']
            content = str(comment.find("div", {"class": "content"}).text).strip()
            time = comment.find("span", {"class": "time"})['title']

            ALL_REPLIES = []
            replies = comment.find_all("li", {"class": "reply"})
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
                    'CommentID': r_comment_id,
                    'User': r_user,
                    'Content': r_content,
                    'Timestamp': r_time
                }
                ALL_REPLIES.append(reply_data)

            main_comment = {
                'CommentID': comment_id,
                'User': user,
                'Content': content,
                'Timestamp': time,
                'hasReplies?': hasReplies,
                'Replies': ALL_REPLIES
            }
            DATA.append(main_comment)
        return DATA


    def comments(self, *, page=1, limit=None):
        URL = f"https://scratch.mit.edu/site-api/comments/user/{self.username}/?page={page}"
        return self._get_comments(URL)[:limit]

    def stats(self):
        try:
            stats= requests.get(
                f"https://scratchdb.lefty.one/v3/user/info/{self.username}"
            ).json()["statistics"]
            stats.pop("ranks")
        except Exception:
            stats = {"loves":-1,"favorites":-1,"comments":-1,"views":-1,"followers":-1,"following":-1}
        return stats

    def ranks(self):
        try:
            return requests.get(
                f"https://scratchdb.lefty.one/v3/user/info/{self.username}"
            ).json()["statistics"]["ranks"]
        except Exception:
            return {"country":{"loves":0,"favorites":0,"comments":0,"views":0,"followers":0,"following":0},"loves":0,"favorites":0,"comments":0,"views":0,"followers":0,"following":0}

    def followers_over_time(self, *, segment=1, range=30):
        return requests.get(f"https://scratchdb.lefty.one/v3/user/graph/{self.username}/followers?segment={segment}&range={range}")

    def forum_counts(self):
        try:
            return requests.get(f"https://scratchdb.lefty.one/v3/forum/user/info/{self.username}").json()["counts"]
        except Exception:
            raise _exceptions.FetchError

    def forum_posts_over_time(self):
        try:
            return requests.get(f"https://scratchdb.lefty.one/v3/forum/user/info/{self.username}").json()["history"]
        except Exception:
            raise _exceptions.FetchError

    def forum_signature(self):
        try:
            return requests.get(f"https://scratchdb.lefty.one/v3/forum/user/info/{self.username}").json()["signature"]
        except Exception:
            raise _exceptions.FetchError

    def forum_signature_history(self):
        return requests.get(f"https://scratchdb.lefty.one/v3/forum/user/history/{self.username}").json()

    def ocular_status(self):
        return requests.get(f"https://my-ocular.jeffalo.net/api/user/{self.username}").json()

    def forum_posts(self, *, page=0, order="newest"):
        try:
            data = requests.get(f"https://scratchdb.lefty.one/v3/forum/user/posts/{self.username}/{page}?o={order}").json()
            return_data = []
            for o in data:
                a = _forum.ForumPost(id = o["id"], _session = self._session)
                a._update_from_dict(o)
                return_data.append(a)
            return return_data
        except Exception:
            return []

# ------ #

def get_user(username):
    try:
        user = User(username=username)
        if user.update() == "429":
            raise(_exceptions.Response429("Your network is blocked or rate-limited by Scratch.\nIf you're using an online IDE like replit.com, try running the code on your computer."))
        return user
    except KeyError:
        return None
    except Exception as e:
        raise(e)
