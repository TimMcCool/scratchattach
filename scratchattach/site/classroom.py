from __future__ import annotations

import json
import warnings
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, TYPE_CHECKING, Any, Callable

import bs4
from bs4 import BeautifulSoup

if TYPE_CHECKING:
    from scratchattach.site.session import Session

from scratchattach.utils.commons import requests
from . import user, activity, typed_dicts
from ._base import BaseSiteComponent
from scratchattach.utils import exceptions, commons
from scratchattach.utils.commons import headers


@dataclass
class Classroom(BaseSiteComponent):
    title: str = ""
    id: int = 0
    classtoken: str = ""

    author: Optional[user.User] = None
    about_class: str = ""
    working_on: str = ""

    is_closed: bool = False
    datetime: datetime = datetime.fromtimestamp(0.0)


    update_function: Callable = field(repr=False, default=requests.get)
    _session: Optional[Session] = field(repr=False, default=None)

    def __post_init__(self):
        # Info on how the .update method has to fetch the data:
        # NOTE: THIS DOESN'T WORK WITH CLOSED CLASSES!
        if self.id:
            self.update_api = f"https://api.scratch.mit.edu/classrooms/{self.id}"
        elif self.classtoken:
            self.update_api = f"https://api.scratch.mit.edu/classtoken/{self.classtoken}"
        else:
            raise KeyError(f"No class id or token provided! {self.__dict__ = }")

        # Headers and cookies:
        if self._session is None:
            self._headers = commons.headers
            self._cookies = {}
        else:
            self._headers = self._session._headers
            self._cookies = self._session._cookies

        # Headers for operations that require accept and Content-Type fields:
        self._json_headers = {**self._headers,
                              "accept": "application/json",
                              "Content-Type": "application/json"}

    def __str__(self) -> str:
        return f"<Classroom {self.title!r}, id={self.id!r}>"

    def update(self):
        try:
            success = super().update()
        except exceptions.ClassroomNotFound:
            success = False

        if not success:
            response = requests.get(f"https://scratch.mit.edu/classes/{self.id}/")
            soup = BeautifulSoup(response.text, "html.parser")

            headings = soup.find_all("h1")
            for heading in headings:
                if heading.text == "Whoops! Our server is Scratch'ing its head":
                    raise exceptions.ClassroomNotFound(f"Classroom id {self.id} is not closed and cannot be found.")

            # id, title, description, status, date_start (iso format), educator/username

            title = soup.find("title").contents[0][:-len(" on Scratch")]

            overviews = soup.find_all("p", {"class": "overview"})
            description, status = overviews[0].text, overviews[1].text

            educator_username = None
            pfx = "Scratch.INIT_DATA.PROFILE = {\n  model: {\n    id: '"
            sfx = "',\n    userId: "
            for script in soup.find_all("script"):
                if pfx in script.text:
                    educator_username = commons.webscrape_count(script.text, pfx, sfx, str)

            ret: typed_dicts.ClassroomDict = {
                "id": self.id,
                "title": title,
                "description": description,
                "educator": {},
                "status": status,
                "is_closed": True
                }

            if educator_username:
                ret["educator"]["username"] = educator_username

            return self._update_from_dict(ret)
        return success

    def _update_from_dict(self, data: typed_dicts.ClassroomDict):
        self.id = int(data["id"])
        self.title = data["title"]
        self.about_class = data["description"]
        self.working_on = data["status"]
        self.datetime = datetime.fromisoformat(data["date_start"])
        self.author = user.User(username=data["educator"]["username"], _session=self._session)
        self.author.supply_data_dict(data["educator"])
        self.is_closed = bool(data["date_end"])
        return True

    def student_count(self) -> int:
        # student count
        text = requests.get(
            f"https://scratch.mit.edu/classes/{self.id}/",
            headers=self._headers
        ).text
        return commons.webscrape_count(text, "Students (", ")")

    def student_names(self, *, page=1) -> list[str]:
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
            found = set("")

            for result in soup.css.select("ul.scroll-content .user a"):
                result_text = result.text.strip()
                if result_text in found:
                    continue
                found.add(result_text)
                ret.append(result_text)

            # for scrollable in soup.find_all("ul", {"class": "scroll-content"}):
            #     if not isinstance(scrollable, Tag):
            #         continue
            #     for item in scrollable.contents:
            #         if not isinstance(item, bs4.NavigableString):
            #             if "user" in item.attrs["class"]:
            #                 anchors = item.find_all("a")
            #                 if len(anchors) == 2:
            #                     ret.append(anchors[1].text.strip())

            return ret

        text = requests.get(
            f"https://scratch.mit.edu/classes/{self.id}/students/?page={page}",
            headers=self._headers
        ).text
        textlist = [i.split('/">')[0] for i in text.split('        <a href="/users/')[1:]]
        return textlist

    def class_studio_count(self) -> int:
        # studio count
        text = requests.get(
            f"https://scratch.mit.edu/classes/{self.id}/",
            headers=self._headers
        ).text
        return commons.webscrape_count(text, "Class Studios (", ")")

    def class_studio_ids(self, *, page: int = 1) -> list[int]:
        """
        Returns the class studio on the class.
        
        Keyword Arguments:
            page: The page of the students that should be returned.
        
        Returns:
            list<int>: The id of the class studios
        """
        if self.is_closed:
            ret = []
            response = requests.get(f"https://scratch.mit.edu/classes/{self.id}/")
            soup = BeautifulSoup(response.text, "html.parser")

            for result in soup.css.select("ul.scroll-content .gallery a[href]:not([class])"):
                value = result["href"]
                if not isinstance(value, str):
                    value = value[0]
                ret.append(commons.webscrape_count(value, "/studios/", "/"))

            # for scrollable in soup.find_all("ul", {"class": "scroll-content"}):
            #     for item in scrollable.contents:
            #         if not isinstance(item, bs4.NavigableString):
            #             if "gallery" in item.attrs["class"]:
            #                 anchor = item.find("a")
            #                 if "href" in anchor.attrs:
            #                     ret.append(commons.webscrape_count(anchor.attrs["href"], "/studios/", "/"))
            return ret

        text = requests.get(
            f"https://scratch.mit.edu/classes/{self.id}/studios/?page={page}",
            headers=self._headers
        ).text
        textlist = [int(i.split('/">')[0]) for i in text.split('<span class="title">\n    <a href="/studios/')[1:]]
        return textlist

    def _check_session(self) -> None:
        if self._session is None:
            raise exceptions.Unauthenticated(
                f"Classroom {self} has no associated session. Use session.connect_classroom() instead of sa.get_classroom()")

    def set_thumbnail(self, thumbnail: bytes) -> None:
        self._check_session()
        requests.post(f"https://scratch.mit.edu/site-api/classrooms/all/{self.id}/",
                      headers=self._headers, cookies=self._cookies,
                      files={"file": thumbnail})

    def set_description(self, desc: str) -> None:
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

    def set_working_on(self, status: str) -> None:
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

    def set_title(self, title: str) -> None:
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

    def add_studio(self, name: str, description: str = '') -> None:
        self._check_session()
        requests.post("https://scratch.mit.edu/classes/create_classroom_gallery/",
                      json={
                          "classroom_id": str(self.id),
                          "classroom_token": self.classtoken,
                          "title": name,
                          "description": description},
                      headers=self._headers, cookies=self._cookies)

    def reopen(self) -> None:
        self._check_session()
        response = requests.put(f"https://scratch.mit.edu/site-api/classrooms/all/{self.id}/",
                                headers=self._headers, cookies=self._cookies,
                                json={"visibility": "visible"})

        try:
            response.json()

        except Exception as e:
            warnings.warn(f"{self._session} may not be authenticated to edit {self}")
            raise e

    def close(self) -> None:
        self._check_session()
        response = requests.post(f"https://scratch.mit.edu/site-api/classrooms/close_classroom/{self.id}/",
                                 headers=self._headers, cookies=self._cookies)

        try:
            response.json()

        except Exception as e:
            warnings.warn(f"{self._session} may not be authenticated to edit {self}")
            raise e

    def register_student(self, username: str, password: str = '', birth_month: Optional[int] = None,
                         birth_year: Optional[int] = None,
                         gender: Optional[str] = None, country: Optional[str] = None, is_robot: bool = False) -> None:
        return register_by_token(self.id, self.classtoken, username, password, birth_month or 1, birth_year or 2000, gender or "(Prefer not to say)", country or "United+States",
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

    def activity(self, student: str = "all", mode: str = "Last created", page: Optional[int] = None) -> list[activity.Activity]:
        """
        Get a list of private activity, only available to the class owner.
        Returns:
            list<activity.Activity> The private activity of users in the class
        """

        self._check_session()

        ascsort, descsort = commons.get_class_sort_mode(mode)

        with requests.no_error_handling():
            try:
                data = requests.get(f"https://scratch.mit.edu/site-api/classrooms/activity/{self.id}/{student}/",
                                    params={"page": page, "ascsort": ascsort, "descsort": descsort},
                                    headers=self._headers, cookies=self._cookies).json()
            except json.JSONDecodeError:
                return []

        _activity: list[activity.Activity] = []
        for activity_json in data:
            _activity.append(activity.Activity(_session=self._session))
            _activity[-1]._update_from_json(activity_json)  # NOT the same as _update_from_dict

        return _activity


def get_classroom(class_id: str) -> Classroom:
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
    warnings.warn(
        "For methods that require authentication, use session.connect_classroom instead of get_classroom\n"
        "If you want to remove this warning, use warnings.filterwarnings('ignore', category=scratchattach.ClassroomAuthenticationWarning)\n"
        "To ignore all warnings of the type GetAuthenticationWarning, which includes this warning, use "
        "`warnings.filterwarnings('ignore', category=scratchattach.GetAuthenticationWarning)`.",
        exceptions.ClassroomAuthenticationWarning
    )
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
    warnings.warn(
        "For methods that require authentication, use session.connect_classroom instead of get_classroom. "
        "If you want to remove this warning, use warnings.filterwarnings('ignore', category=ClassroomAuthenticationWarning). "
        "To ignore all warnings of the type GetAuthenticationWarning, which includes this warning, use "
        "warnings.filterwarnings('ignore', category=GetAuthenticationWarning).",
        exceptions.ClassroomAuthenticationWarning
    )
    return commons._get_object("classtoken", class_token, Classroom, exceptions.ClassroomNotFound)


def register_by_token(class_id: int, class_token: str, username: str, password: str, birth_month: int, birth_year: int,
                      gender: str, country: str, is_robot: bool = False) -> None:
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
                             data=data, headers=commons.headers, cookies={"scratchcsrftoken": 'a'})
    ret = response.json()[0]

    if "username" in ret:
        return
    else:
        raise exceptions.Unauthorized(f"Can't create account: {response.text}")
