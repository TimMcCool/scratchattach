import datetime
import warnings
from typing import TYPE_CHECKING

import bs4

if TYPE_CHECKING:
    from ..site.session import Session

from ..utils.commons import requests
from . import user, activity
from ._base import BaseSiteComponent
from ..utils import exceptions, commons
from ..utils.commons import headers

from bs4 import BeautifulSoup


class Classroom(BaseSiteComponent):
    def __init__(self, **entries):
        # Info on how the .update method has to fetch the data:
        # NOTE: THIS DOESN'T WORK WITH CLOSED CLASSES!
        self.update_function = requests.get
        if "id" in entries:
            self.update_API = f"https://api.scratch.mit.edu/classrooms/{entries['id']}"
        elif "classtoken" in entries:
            self.update_API = f"https://api.scratch.mit.edu/classtoken/{entries['classtoken']}"
        else:
            raise KeyError(f"No class id or token provided! Entries: {entries}")

        # Set attributes every Project object needs to have:
        self._session: Session = None
        self.id = None
        self.classtoken = None

        self.__dict__.update(entries)

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

    def __repr__(self):
        return f"classroom called '{self.title}'"

    def update(self):
        try:
            success = super().update()
        except exceptions.ClassroomNotFound:
            success = False

        if not success:
            response = requests.get(f"https://scratch.mit.edu/classes/{self.id}/")
            soup = BeautifulSoup(response.text, "html.parser")
            # id, title, description, status, date_start (iso str), educator/username
            title = soup.find("title").contents[0][:-len(" on Scratch")]

            overviews = soup.find_all("p", {"class": "overview"})
            description, status = overviews[0].text, overviews[1].text

            educator_username = None
            pfx = "Scratch.INIT_DATA.PROFILE = {\n  model: {\n    id: '"
            sfx = "',\n    userId: "
            for script in soup.find_all("script"):
                if pfx in script.text:
                    educator_username = commons.webscrape_count(script.text, pfx, sfx, str)

            ret = {"id": self.id,
                   "title": title,
                   "description": description,
                   "status": status,
                   "educator": {"username": educator_username},
                   "is_closed": True
                   }

            return self._update_from_dict(ret)
        return success

    def _update_from_dict(self, classrooms):
        try:
            self.id = int(classrooms["id"])
        except Exception:
            pass
        try:
            self.title = classrooms["title"]
        except Exception:
            pass
        try:
            self.about_class = classrooms["description"]
        except Exception:
            pass
        try:
            self.working_on = classrooms["status"]
        except Exception:
            pass
        try:
            self.datetime = datetime.datetime.fromisoformat(classrooms["date_start"])
        except Exception:
            pass
        try:
            self.author = user.User(username=classrooms["educator"]["username"], _session=self._session)
        except Exception:
            pass
        try:
            self.author._update_from_dict(classrooms["educator"])
        except Exception:
            pass
        self.is_closed = classrooms.get("is_closed", False)
        return True

    def student_count(self):
        # student count
        text = requests.get(
            f"https://scratch.mit.edu/classes/{self.id}/",
            headers=self._headers
        ).text
        return commons.webscrape_count(text, "Students (", ")")

    def student_names(self, *, page=1):
        """
        Returns the student on the class.
        
        Keyword Arguments:
            page: The page of the students that should be returned.
        
        Returns:
            list<str>: The usernames of the class students
        """
        if self.is_closed:
            ret = []
            response = requests.get(f"https://scratch.mit.edu/classes/{self.id}/")
            soup = BeautifulSoup(response.text, "html.parser")

            for scrollable in soup.find_all("ul", {"class": "scroll-content"}):
                if len(scrollable.contents) > 0:
                    for item in scrollable.contents:
                        if not isinstance(item, bs4.NavigableString):
                            if "user" in item.attrs["class"]:
                                anchors = item.find_all("a")
                                if len(anchors) == 2:
                                    ret.append(anchors[1].text.strip())

            return ret

        text = requests.get(
            f"https://scratch.mit.edu/classes/{self.id}/students/?page={page}",
            headers=self._headers
        ).text
        textlist = [i.split('/">')[0] for i in text.split('        <a href="/users/')[1:]]
        return textlist

    def class_studio_count(self):
        # studio count
        text = requests.get(
            f"https://scratch.mit.edu/classes/{self.id}/",
            headers=self._headers
        ).text
        return commons.webscrape_count(text, "Class Studios (", ")")

    def class_studio_ids(self, *, page=1) -> list[int]:
        """
        Returns the class studio on the class.
        
        Keyword Arguments:
            page: The page of the students that should be returned.
        
        Returns:
            list<str>: The id of the class studios
        """
        if self.is_closed:
            ret = []
            response = requests.get(f"https://scratch.mit.edu/classes/{self.id}/")
            soup = BeautifulSoup(response.text, "html.parser")

            for scrollable in soup.find_all("ul", {"class": "scroll-content"}):
                if len(scrollable.contents) > 0:
                    for item in scrollable.contents:
                        if not isinstance(item, bs4.NavigableString):
                            if "gallery" in item.attrs["class"]:
                                anchor = item.find("a")
                                if "href" in anchor.attrs:
                                    ret.append(commons.webscrape_count(anchor.attrs["href"], "/studios/", "/"))
            return ret

        text = requests.get(
            f"https://scratch.mit.edu/classes/{self.id}/studios/?page={page}",
            headers=self._headers
        ).text
        textlist = [int(i.split('/">')[0]) for i in text.split('<span class="title">\n    <a href="/studios/')[1:]]
        return textlist

    def _check_session(self):
        if self._session is None:
            raise exceptions.Unauthenticated(
                f"Classroom {self} has no associated session. Use session.connect_classroom() instead of sa.get_classroom()")

    def set_thumbnail(self, thumbnail: bytes):
        self._check_session()
        requests.post(f"https://scratch.mit.edu/site-api/classrooms/all/{self.id}/",
                      headers=self._headers, cookies=self._cookies,
                      files={"file": thumbnail})

    def set_description(self, desc: str):
        self._check_session()
        response = requests.put(f"https://scratch.mit.edu/site-api/classrooms/all/{self.id}/",
                                headers=self._headers, cookies=self._cookies,
                                json={"description": desc})

        try:
            data = response.json()
            if data["description"] == desc:
                # Success!
                return
            else:
                warnings.warn(f"{self._session} may not be authenticated to edit {self}")

        except Exception as e:
            warnings.warn(f"{self._session} may not be authenticated to edit {self}")
            raise e

    def set_working_on(self, status: str):
        self._check_session()
        response = requests.put(f"https://scratch.mit.edu/site-api/classrooms/all/{self.id}/",
                                headers=self._headers, cookies=self._cookies,
                                json={"status": status})

        try:
            data = response.json()
            if data["status"] == status:
                # Success!
                return
            else:
                warnings.warn(f"{self._session} may not be authenticated to edit {self}")

        except Exception as e:
            warnings.warn(f"{self._session} may not be authenticated to edit {self}")
            raise e

    def set_title(self, title: str):
        self._check_session()
        response = requests.put(f"https://scratch.mit.edu/site-api/classrooms/all/{self.id}/",
                                headers=self._headers, cookies=self._cookies,
                                json={"title": title})

        try:
            data = response.json()
            if data["title"] == title:
                # Success!
                return
            else:
                warnings.warn(f"{self._session} may not be authenticated to edit {self}")

        except Exception as e:
            warnings.warn(f"{self._session} may not be authenticated to edit {self}")
            raise e

    def reopen(self):
        self._check_session()
        response = requests.put(f"https://scratch.mit.edu/site-api/classrooms/all/{self.id}/",
                                headers=self._headers, cookies=self._cookies,
                                json={"visibility": "visible"})

        try:
            response.json()
        except Exception as e:
            warnings.warn(f"{self._session} may not be authenticated to edit {self}")
            raise e

    def close(self):
        self._check_session()
        response = requests.post(f"https://scratch.mit.edu/site-api/classrooms/close_classroom/{self.id}/",
                                 headers=self._headers, cookies=self._cookies)

        try:
            response.json()
        except Exception as e:
            warnings.warn(f"{self._session} may not be authenticated to edit {self}")
            raise e

    def register_student(self, username: str, password: str = '', birth_month: int = None, birth_year: int = None,
                         gender: str = None, country: str = None, is_robot: bool = False):
        return register_by_token(self.id, self.classtoken, username, password, birth_month, birth_year, gender, country,
                                 is_robot)

    def generate_signup_link(self):
        if self.classtoken is not None:
            return f"https://scratch.mit.edu/signup/{self.classtoken}"

        self._check_session()

        response = requests.get(f"https://scratch.mit.edu/site-api/classrooms/generate_registration_link/{self.id}/",
                                headers=self._headers, cookies=self._cookies)
        # Should really check for '404' page
        data = response.json()
        if "reg_link" in data:
            return data["reg_link"]
        else:
            raise exceptions.Unauthorized(f"{self._session} is not authorised to generate a signup link of {self}")

    def public_activity(self, *, limit=20):
        """
        Returns:
            list<scratchattach.Activity>: The user's activity data as parsed list of scratchattach.activity.Activity objects
        """
        if limit > 20:
            warnings.warn("The limit is set to more than 20. There may be an error")
        soup = BeautifulSoup(
            requests.get(f"https://scratch.mit.edu/site-api/classrooms/activity/public/{self.id}/?limit={limit}").text,
            'html.parser')

        activities = []
        source = soup.find_all("li")

        for data in source:
            _activity = activity.Activity(_session=self._session, raw=data)
            _activity._update_from_html(data)
            activities.append(_activity)

        return activities

    def activity(self, student: str = "all", mode: str = "Last created", page: int = None):
        """
        Get a list of actvity raw dictionaries. However, they are in a very annoying format. This method should be updated
        """

        self._check_session()

        ascsort, descsort = commons.get_class_sort_mode(mode)

        data = requests.get(f"https://scratch.mit.edu/site-api/classrooms/activity/{self.id}/{student}/",
                            params={"page": page, "ascsort": ascsort, "descsort": descsort},
                            headers=self._headers, cookies=self._cookies).json()

        return data


def get_classroom(class_id) -> Classroom:
    """
    Gets a class without logging in.

    Args:
        class_id (str): class id of the requested class

    Returns:
        scratchattach.classroom.Classroom: An object representing the requested classroom

    Warning:
        Any methods that require authentication will not work on the returned object.

        If you want to use these, get the user with :meth:`scratchattach.session.Session.connect_classroom` instead.
    """
    warnings.warn("For methods that require authentication, use session.connect_classroom instead of get_classroom")
    return commons._get_object("id", class_id, Classroom, exceptions.ClassroomNotFound)


def get_classroom_from_token(class_token) -> Classroom:
    """
    Gets a class without logging in.

    Args:
        class_token (str): class token of the requested class

    Returns:
        scratchattach.classroom.Classroom: An object representing the requested classroom

    Warning:
        Any methods that require authentication will not work on the returned object.

        If you want to use these, get the user with :meth:`scratchattach.session.Session.connect_classroom` instead.
    """
    warnings.warn("For methods that require authentication, use session.connect_classroom instead of get_classroom")
    return commons._get_object("classtoken", class_token, Classroom, exceptions.ClassroomNotFound)


def register_by_token(class_id: int, class_token: str, username: str, password: str, birth_month: int, birth_year: int,
                      gender: str, country: str, is_robot: bool = False):
    data = {"classroom_id": class_id,
            "classroom_token": class_token,

            "username": username,
            "password": password,
            "birth_month": birth_month,
            "birth_year": birth_year,
            "gender": gender,
            "country": country,
            "is_robot": is_robot}

    response = requests.post("https://scratch.mit.edu/classes/register_new_student/",
                             data=data, headers=headers, cookies={"scratchcsrftoken": 'a'})
    ret = response.json()[0]

    if "username" in ret:
        return
    else:
        raise exceptions.Unauthorized(f"Can't create account: {response.text}")
