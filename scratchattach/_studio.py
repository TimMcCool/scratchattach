#----- Getting studios

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

class Studio:

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
        self._json_headers = self._headers
        self._json_headers["accept"] = "application/json"
        self._json_headers["Content-Type"] = "application/json"

    def update(self):
        studio = requests.get(f"https://api.scratch.mit.edu/studios/{self.id}")
        if "429" in str(studio):
            return "429"
        if studio.text == '{\n  "response": "Too many requests"\n}':
            return "429"
        studio = studio.json()
        return self._update_from_dict(studio)

    def _update_from_dict(self, studio):
        self.id = int(studio["id"])
        self.title = studio["title"]
        self.description = studio["description"]
        self.host_id = studio["host"]
        self.open_to_all = studio["open_to_all"]
        self.comments_allowed = studio["comments_allowed"]
        self.image_url = studio["image"]
        self.created = studio["history"]["created"]
        self.modified = studio["history"]["modified"]
        self.follower_count = studio["stats"]["followers"]
        self.manager_count = studio["stats"]["managers"]
        self.project_count = studio["stats"]["projects"]


    def follow(self):
        requests.put(
            f"https://scratch.mit.edu/site-api/users/bookmarkers/{self.id}/add/?usernames={self._session._username}",
            headers = headers,
            cookies = self._cookies,
        )

    def unfollow(self):
        requests.put(
            f"https://scratch.mit.edu/site-api/users/bookmarkers/{self.id}/remove/?usernames={self._session._username}",
            headers = headers,
            cookies = self._cookies,
        )

    def comments(self, *, limit=40, offset=0):
        comments = []
        while len(comments) < limit:
            r = requests.get(
                f"https://api.scratch.mit.edu/studios/{self.id}/comments/?limit={min(40, limit-len(comments))}&offset={offset}"
            ).json()
            if len(r) != 40:
                break
            offset += 40
            comments = comments + r
        return comments

    def get_comment_replies(self, *, comment_id, limit=40, offset=0):
        comments = []
        while len(comments) < limit:
            r = requests.get(
                f"https://api.scratch.mit.edu/studios/{self.id}/comments/{comment_id}/replies?limit={min(40, limit-len(comments))}&offset={offset}"
            ).json()
            if len(r) != 40:
                break
            offset += 40
            comments = comments + r
        return comments


    def post_comment(self, content, *, parent_id="", commentee_id=""):
        if self._headers is None:
            raise(_exceptions.Unauthenticated)
            return
        data = {
            "commentee_id": commentee_id,
            "content": content,
            "parent_id": parent_id,
        }
        headers = self._json_headers
        headers["referer"] = "https://scratch.mit.edu/projects/" + str(self.id) + "/"
        return json.loads(requests.post(
            f"https://api.scratch.mit.edu/proxy/comments/studio/{self.id}/",
            headers = headers,
            cookies = self._cookies,
            data=json.dumps(data),
        ).text)


    def reply_comment(self, content, *, parent_id, commentee_id=""):
        return self.post_comment(content, parent_id=parent_id, commentee_id=commentee_id)

    def projects(self, limit=40, offset=0):
        return requests.get(f"https://api.scratch.mit.edu/studios/{self.id}/projects/?limit={limit}&offset={offset}").json()

    def curators(self, limit=24, offset=0):
        if limit>24:
            limit=24
        raw_curators = requests.get(f"https://api.scratch.mit.edu/studios/{self.id}/curators/?limit={limit}&offset={offset}").json()
        curators = []
        for c in raw_curators:
            u = _user.User(username=c["username"], session=self._session)
            u._update_from_dict(c)
            curators.append(u)
        return curators


    def invite_curator(self, curator):
        try:
            return requests.put(
                f"https://scratch.mit.edu/site-api/users/curators-in/{self.id}/invite_curator/?usernames={curator}",
                headers = headers,
                cookies = self._cookies,
            ).json()
        except Exception:
            raise(_exceptions.Unauthorized)

    def promote_curator(self, curator):
        try:
            return requests.put(
                f"https://scratch.mit.edu/site-api/users/curators-in/{self.id}/promote/?usernames={curator}",
                headers = headers,
                cookies = self._cookies
            ).json()
        except Exception:
            raise(_exceptions.Unauthorized)


    def remove_curator(self, curator):
        try:
            return requests.put(
                f"https://scratch.mit.edu/site-api/users/curators-in/{self.id}/remove/?usernames={curator}",
                headers = headers,
                cookies = self._cookies
            ).json()
        except Exception:
            raise(_exceptions.Unauthorized)

    def leave(self):
        return self.remove_curator(self._session._username)

    def add_project(self, project_id):
        return requests.post(
            f"https://api.scratch.mit.edu/studios/{self.id}/project/{project_id}",
            headers = self._headers
        ).json()

    def remove_project(self, project_id):
        return requests.delete(
            f"https://api.scratch.mit.edu/studios/{self.id}/project/{project_id}",
            headers = self._headers
        ).json()

    def managers(self, limit=24, offset=0):
        if limit>24:
            limit=24
        raw_m = requests.get(f"https://api.scratch.mit.edu/studios/{self.id}/managers/?limit={limit}&offset={offset}").json()
        managers = []
        for c in raw_m:
            u = _user.User(username=c["username"], _session=self._session)
            u._update_from_dict(c)
            managers.append(u)
        return managers

    def set_description(self, new):
        requests.put(
            f"https://scratch.mit.edu/site-api/galleries/all/{self.id}/",
            headers = headers,
            cookies = self._cookies,
            data=json.dumps({"description":new+"\n"})
        )

    def set_title(self, new):
        requests.put(
            f"https://scratch.mit.edu/site-api/galleries/all/{self.id}/",
            headers = headers,
            cookies = self._cookies,
            data=json.dumps({"title":new}))

    def open_projects(self):
        requests.put(
            f"https://scratch.mit.edu/site-api/galleries/{self.id}/mark/open/",
            headers = headers,
            cookies = self._cookies,
        )


    def close_projects(self):
        requests.put(
            f"https://scratch.mit.edu/site-api/galleries/{self.id}/mark/closed/",
            headers = headers,
            cookies = self._cookies,
        )

    def turn_off_commenting(self):
        if self.comments_allowed:
            requests.post(
                f"https://scratch.mit.edu/site-api/comments/gallery/{self.id}/toggle-comments/",
                headers = headers,
                cookies = self._cookies,

            )
            self.comments_allowed = not self.comments_allowed

    def turn_on_commenting(self):
        if not self.comments_allowed:
            requests.post(
                f"https://scratch.mit.edu/site-api/comments/gallery/{self.id}/toggle-comments/",
                headers = headers,
                cookies = self._cookies,

            )
            self.comments_allowed = not self.comments_allowed

    def toggle_commenting(self):
        requests.post(
            f"https://scratch.mit.edu/site-api/comments/gallery/{self.id}/toggle-comments/",
            headers = headers,
            cookies = self._cookies,
        )
        self.comments_allowed = not self.comments_allowed

    def activity(self, *, limit=20, offset=0):
        if limit>40:
            limit=40
        return requests.get(
            f"https://api.scratch.mit.edu/studios/{self.id}/activity/?limit={limit}&offset={offset}",
            headers = headers
        ).json()


def get_studio(studio_id):
    try:
        studio = Studio(id=int(studio_id))
        if studio.update() == "429":
            raise(_exceptions.Response429("Your network is blocked or rate-limited by Scratch.\nIf you're using an online IDE like replit.com, try running the code on your computer."))
        return studio
    except KeyError:
        return None
    except Exception as e:
        raise(e)
