"""v2 ready: Session class and login function"""

import json
import requests
from . import project
from . import exceptions
from . import studio
from . import forum
from bs4 import BeautifulSoup
from .abstractscratch import AbstractScratch
from .commons import headers
from . import commons
from . import comment
from . import activity

class User(AbstractScratch):

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

    def __str__(self):
        return str(self.username)

    def __init__(self, **entries):

        # Info on how the .update method has to fetch the data:
        self.update_function = requests.get
        self.update_API = f"https://api.scratch.mit.edu/users/{entries['username']}"

        # Set attributes every User object needs to have:
        self._session = None
        self.id = None
        self.username = None
        self.name = None

        # Update attributes from entries dict:
        entries.setdefault("name", entries.get("username"))
        self.__dict__.update(entries)

        # Set alternative attributes:
        if hasattr(self, "bio"):
            self.about_me = self.bio
        if hasattr(self, "status"):
            self.wiwo = self.status
        if hasattr(self, "name"):
            self.username = self.name

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
        try: self.id = data["id"]
        except KeyError: pass
        try: self.scratchteam = data["scratchteam"]
        except KeyError: pass
        try: self.join_date = data["history"]["joined"]
        except KeyError: pass
        try: self.about_me = data["profile"]["bio"]
        except KeyError: pass
        try: self.wiwo = data["profile"]["status"]
        except KeyError: pass
        try: self.country = data["profile"]["country"]
        except KeyError: pass
        try: self.icon_url = data["profile"]["images"]["90x90"]
        except KeyError: pass
        return True

    def _assert_permission(self):
        self._assert_auth()
        if self._session._username != self.username:
            raise exceptions.Unauthorized(
                "You need to be authenticated as the profile owner to do this.")


    def does_exist(self):
        """
        Returns:
            boolean : True if the user exists, False if the user is deleted, None if an error occured
        """
        if requests.get(f"https://scratch.mit.edu/users/{self.username}/").status_code == 200:
            return True
        if requests.get(f"https://scratch.mit.edu/users/{self.username}/").status_code == 404:
            return False

    def is_new_scratcher(self):
        """
        Returns:
            boolean : True if the user has the New Scratcher status, else False
        """
        try:
            res = requests.get(f"https://scratch.mit.edu/users/{self.username}/").text
            group=res[res.rindex('<span class="group">'):][:70]
            return "new scratcher" in group.lower()
        except Exception:
            return None

    def message_count(self):

        return json.loads(requests.get(f"https://api.scratch.mit.edu/users/{self.username}/messages/count/", headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.3c6 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',}).text)["count"]

    def featured_data(self):
        """
        Returns:
            dict: Gets info on the user's featured project and featured label (like "Featured project", "My favorite things", etc.)
        """
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
            headers = self._headers
        ).text
        return commons.webscrape_count(text, "Followers (", ")")

    def following_count(self):
        # following count
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

    def is_following(self, user):
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
                if following_names == []:
                    break
                offset += 20
            except Exception:
                print("Warning: API error when performing following check")
                return following
        return following

    def is_followed_by(self, user):
        """
        Returns:
            boolean: Whether the user is followed by the user provided as argument
        """
        return User(username=user).is_following(self.username)

    def project_count(self):
        text = requests.get(
            f"https://scratch.mit.edu/users/{self.username}/projects/",
            headers = self._headers
        ).text
        return commons.webscrape_count(text, "Shared Projects (", ")")

    def studio_count(self):
        text = requests.get(
            f"https://scratch.mit.edu/users/{self.username}/studios/",
            headers = self._headers
        ).text
        return commons.webscrape_count(text, "Studios I curate (", ")")

    def studios_following_count(self):
        text = requests.get(
            f"https://scratch.mit.edu/users/{self.username}/studios/",
            headers = self._headers
        ).text
        return commons.webscrape_count(text, "Studios I follow (", ")")

    def studios(self, *, limit=40, offset=0):
        _studios = commons.api_iterative(
            f"https://api.scratch.mit.edu/users/{self.username}/studios/curate", limit=limit, offset=offset)
        studios = []
        for studio_dict in _studios:
            _studio = studio.Studio(_session = self._session, id = studio_dict["id"])
            _studio._update_from_dict(studio_dict)
            studios.append(_studio)
        return studios

    def projects(self, *, limit=40, offset=0):
        """
        Returns:
            list<projects.projects.Project>: The user's shared projects
        """
        _projects = commons.api_iterative(
            f"https://api.scratch.mit.edu/users/{self.username}/projects/", limit=limit, offset=offset, headers = self._headers)
        for p in _projects:
            p["author"] = {"username":self.username}
        return commons.parse_object_list(_projects, project.Project, self._session)

    def favorites(self, *, limit=None, offset=0):
        """
        Returns:
            list<projects.projects.Project>: The user's favorite projects
        """
        _projects = commons.api_iterative(
            f"https://api.scratch.mit.edu/users/{self.username}/favorites/", limit=limit, offset=offset, headers = self._headers)
        return commons.parse_object_list(_projects, project.Project, self._session)

    def favorites_count(self):
        text = requests.get(
            f"https://scratch.mit.edu/users/{self.username}/favorites/",
            headers = self._headers
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
            f"https://api.scratch.mit.edu/users/{self.username}/projects/recentlyviewed", limit=limit, offset=offset, headers = self._headers)
        return commons.parse_object_list(_projects, project.Project, self._session)

    def set_bio(self, text):
        """
        Sets the user's "About me" section. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_user`
        """
        self._assert_permission()
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
        """
        Sets the user's "What I'm working on" section. You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_user`
        """
        self._assert_permission()
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
            headers = self._json_headers,
            cookies = self._cookies,
            data = json.dumps({"featured_project":int(project_id),"featured_project_label":label})
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
            content: Content of the comment that should be posted

        Keyword Arguments:
            parent_id: ID of the comment you want to reply to. If you don't want to mention a user, don't put the argument.
            commentee_id: ID of the user that will be mentioned in your comment and will receive a message about your comment. If you don't want to mention a user, don't put the argument.

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
            headers = headers,
            cookies = self._cookies,
            data=json.dumps(data),
        )
        if r.status_code != 200:
            raise exceptions.CommentPostFailure(r.text)

        try:
            text = r.text
            data = {
                'id': text.split('<div id="comments-')[1].split('" class="comment')[0],
                'author': {"username":text.split('" data-comment-user="')[1].split('"><img class')[0]},
                'content': text.split('<div class="content">')[1].split('"</div>')[0],
                'reply_count': 0,
                'cached_replies': []
            }
            _comment = comment.Comment(source="profile", source_id=self.username, id=data["id"], _session = self._session)
            _comment._update_from_dict(data)
            return _comment
        except Exception:
            if '{"error": "isFlood"}' in text:
                raise(exceptions.CommentPostFailure(
                    "You are being rate-limited for running this operation too often. Implement a cooldown of about 10 seconds."))
            else:
                raise(exceptions.FetchError("Couldn't parse API response"))

    def reply_comment(self, content, *, parent_id, commentee_id=""):
        """
        Replies to a comment given by its id

        Args:
            content: Content of the comment that should be posted

        Keyword Arguments:
            parent_id: ID of the comment you want to reply to
            commentee_id: ID of the user that will be mentioned in your comment and will receive a message about your comment. If you don't want to mention a user, don't put the argument.
        """
        return self.post_comment(content, parent_id=parent_id, commentee_id=commentee_id)

    def activity(self, *, limit=1000):
        """
        Returns:
            list<scratchattach.Activity>: The user's activity data as parsed list of scratchattach.activity.Activity objects
        """
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
        self._assert_permission()
        return requests.post(
            f"https://scratch.mit.edu/site-api/comments/user/{self.username}/rep/",
            headers = headers,
            cookies = self._cookies,
            data = json.dumps({"id":str(comment_id)})
        )

    def comments(self, *, page=1, limit=None):
        """
        Returns the comments posted on the user's profile (with replies).

        Keyword Arguments:
            page: The page of the comments that should be returned.
            limit: Max. amount of returned comments.

        Returns:
            list<dict>: A list containing the requested comments as dicts.
        """
        URL = f"https://scratch.mit.edu/site-api/comments/user/{self.username}/?page={page}"
        DATA = []

        page_contents = requests.get(URL).content

        soup = BeautifulSoup(page_contents, "html.parser")

        _comments = soup.find_all("li", {"class": "top-level-reply"})

        if len(_comments) == 0:
            return None

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
            _comment = comment.Comment(source="profile", source_id=self.username, _session = self._session)
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
                    'author':{'username': r_user},
                    'content': r_content,
                    'datetime_created': r_time,
                    "parent_id" : comment_id,
                    "cached_parent_comment" : _comment,
                }
                _r_comment = comment.Comment(source="profile", source_id=self.username, _session = self._session)
                _r_comment._update_from_dict(reply_data)
                ALL_REPLIES.append(_r_comment)

            _comment.reply_count = len(ALL_REPLIES)
            _comment.cached_replies = list(ALL_REPLIES)

            DATA.append(_comment)
        return DATA

    def comment_by_id(self, comment_id):
        """
        Gets a comment on this user's profile by id.

        Warning:
            For comments very far down on the user's profile, this method will take a while to find the comment. Very old comment are deleted from Scratch's database and may not appear.
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
        return None

    def stats(self):
        """
        Gets information about the user's stats. Fetched from ScratchDB.

        Warning:
            ScratchDB is down indefinitely, therefore this method is deprecated.

        Returns:
            dict: A dict containing the user's stats. If the stats aren't available, all values will be -1.
        """
        print("Warning: ScratchDB is down indefinitely, therefore this method is deprecated.")
        try:
            stats= requests.get(
                f"https://scratchdb.lefty.one/v3/user/info/{self.username}"
            ).json()["statistics"]
            stats.pop("ranks")
        except Exception:
            stats = {"loves":-1,"favorites":-1,"comments":-1,"views":-1,"followers":-1,"following":-1}
        return stats

    def ranks(self):
        """
        Gets information about the user's ranks. Fetched from ScratchDB.

        Warning:
            ScratchDB is down indefinitely, therefore this method is deprecated.

        Returns:
            dict: A dict containing the user's ranks. If the ranks aren't available, all values will be -1.
        """
        print("Warning: ScratchDB is down indefinitely, therefore this method is deprecated.")
        try:
            return requests.get(
                f"https://scratchdb.lefty.one/v3/user/info/{self.username}"
            ).json()["statistics"]["ranks"]
        except Exception:
            return {"country":{"loves":0,"favorites":0,"comments":0,"views":0,"followers":0,"following":0},"loves":0,"favorites":0,"comments":0,"views":0,"followers":0,"following":0}

    def followers_over_time(self, *, segment=1, range=30):
        """
        Gets information about the user's follower count history. Fetched from ScratchDB.

        Warning:
            ScratchDB is down indefinitely, therefore this method is deprecated.

        Keyword Args:
            segment (int): Offset for the first returned element.
            range (int): Amount of returned elements.

        Returns:
            list<dict>
        """
        print("Warning: ScratchDB is down indefinitely, therefore this method is deprecated.")
        return requests.get(f"https://scratchdb.lefty.one/v3/user/graph/{self.username}/followers?segment={segment}&range={range}")

    def forum_counts(self):
        print("Warning: ScratchDB is down indefinitely, therefore this method is deprecated.")
        try:
            return requests.get(f"https://scratchdb.lefty.one/v3/forum/user/info/{self.username}").json()["counts"]
        except Exception:
            raise exceptions.FetchError

    def forum_posts_over_time(self):
        print("Warning: ScratchDB is down indefinitely, therefore this method is deprecated.")
        try:
            return requests.get(f"https://scratchdb.lefty.one/v3/forum/user/info/{self.username}").json()["history"]
        except Exception:
            raise exceptions.FetchError

    def forum_signature(self):
        print("Warning: ScratchDB is down indefinitely, therefore this method is deprecated.")
        try:
            return requests.get(f"https://scratchdb.lefty.one/v3/forum/user/info/{self.username}").json()["signature"]
        except Exception:
            raise exceptions.FetchError

    def forum_signature_history(self):
        print("Warning: ScratchDB is down indefinitely, therefore this method is deprecated.")
        return requests.get(f"https://scratchdb.lefty.one/v3/forum/user/history/{self.username}").json()

    def ocular_status(self):
        """
        Gets information about the user's ocular status. Ocular is a website developed by jeffalo: https://ocular.jeffalo.net/

        Returns:
            dict
        """
        return requests.get(f"https://my-ocular.jeffalo.net/api/user/{self.username}").json()

    ''' WIP
    def forum_posts(self, *, page=0, order="newest"):
        """
        Gets the forum posts associated with the user.

        Args:
            username (str): Username of the requested user

        Keyword Args:
            page (int): Search the page of the results that should be returned.
            order (str): Specifies the order of the returned posts. "newest" means the first returned post is the newest one, "oldest" means it is the oldest one.

        Returns:
            list<scratchattach.forum.ForumPost>: A list that contains the forum posts associated with the user.
        """
        try:
            data = requests.get(f"https://scratchdb.lefty.one/v3/forum/user/posts/{self.username}/{page}?o={order}").json()
            return_data = []
            for o in data:
                a = forum.ForumPost(id = o["id"], _session = self._session)
                a._update_from_dict(o)
                return_data.append(a)
            return return_data
        except Exception:
            return []'''

# ------ #

def get_user(username):
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
    return commons._get_object("username", username, User, exceptions.UserNotFound)
