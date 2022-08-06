#----- Getting forum topics and posts

import json
import requests
from . import _user
from . import _exceptions

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
    "x-csrftoken": "a",
    "x-requested-with": "XMLHttpRequest",
    "referer": "https://scratch.mit.edu",
}

class ForumTopic:

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

    def update(self):
        topic = requests.get(f"https://scratchdb.lefty.one/v3/forum/topic/info/{self.id}").json()
        return self._update_from_dict(topic)

    def _update_from_dict(self, topic):
        self.title = topic["title"]
        self.category = topic["category"]
        if topic["closed"] == 1:
            self.closed = True
        else:
            self.closed = False
        if topic["deleted"] == 1:
            self.deleted = True
        else:
            self.deleted = False
        self.post_count = topic["post_count"]

    def activity(self):
        return requests.get(f"https://scratchdb.lefty.one/v3/forum/topic/history/{self.id}").json()

    def post_count_by_user(self, username):
        data = requests.get(f"https://scratchdb.lefty.one/v3/forum/topic/graph/{self.id}/{username}?segment=1&range=1").json()
        if len(data) == 0:
            return 0
        else:
            return data[0]["value"]

    def posts(self, *, page=0, order="oldest"):
        data = requests.get(f"https://scratchdb.lefty.one/v3/forum/topic/posts/{self.id}/{page}?o={order}").json()
        return_data = []
        for o in data:
            a = ForumPost(id = o["id"], _session = self._session)
            a._update_from_dict(o)
            return_data.append(a)
        return return_data

    def first_post(self):
        o = requests.get(f"https://scratchdb.lefty.one/v3/forum/topic/posts/{self.id}/0?o=oldest").json()[0]
        a = ForumPost(id = o["id"], _session = self._session)
        a._update_from_dict(o)
        return a


class ForumPost:

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


    def update(self):
        post = requests.get(f"https://scratchdb.lefty.one/v3/forum/post/info/{self.id}").json()
        return self._update_from_dict(post)

    def _update_from_dict(self, post):
        self.author = post["username"]
        self.posted = post["time"]["posted"]
        self.edited = post["time"]["edited"]
        self.edited_by = post["editor"]
        if post["deleted"] == 1:
            self.deleted = True
        else:
            self.deleted = False
        self.html_content = post["content"]["html"]
        self.bb_content = post["content"]["bb"]
        self.topic_id = post["topic"]["id"]
        self.topic_name = post["topic"]["title"]
        self.topic_category = post["topic"]["category"]

    def get_topic(self):
        t = ForumTopic(id = self.topic_id, _session = self._session)
        t.update()
        return t

    def ocular_reactions(self):
        return requests.get(f"https://my-ocular.jeffalo.net/api/reactions/{self.id}").json()

    def get_author(self):
        u = _user.User(username=self.author, _session = self._session)
        u.update()
        return u

    def edit(self, new_content):

        cookies = self._cookies
        cookies["accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
        cookies["Content-Type"] = "application/x-www-form-urlencoded"

        r = requests.post(
            f"https://scratch.mit.edu/discuss/post/{self.id}/edit/",
            headers = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "accept-language": "de,en;q=0.9",
                "cache-control": "max-age=0",
                "content-type": "application/x-www-form-urlencoded",
                "sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"101\", \"Google Chrome\";v=\"101\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Windows\"",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1",
                "Referer": f"https://scratch.mit.edu/discuss/post/{self.id}/edit/",
                "x-csrftoken": "a"
            },
            cookies = cookies,
            json = f"csrfmiddlewaretoken=a&body={new_content}&"
        )


def get_topic(topic_id):

    """
    Gets a forum topic
    """

    try:
        topic = ForumTopic(id=int(topic_id))
        topic.update()
        return topic
    except KeyError:
        return None

def get_topic_list(category_name, *, page=0, include_deleted=False):
    category_name.replace(" ", "%20")
    if include_deleted:
        filter = 0
    else:
        filter = 1
    try:
        data = requests.get(f"https://scratchdb.lefty.one/v3/forum/category/topics/{category_name}/{page}?detail=1&filter={filter}").json()
        return_data = []
        for topic in data:
            t = ForumTopic(id = topic["id"])
            t._update_from_dict(topic)
            return_data.append(t)
        return return_data
    except Exception:
        return None

def get_post(post_id):

    """
    Gets a forum post
    """

    try:
        post = ForumPost(id=int(post_id))
        post.update()
        return post
    except KeyError:
        return None
