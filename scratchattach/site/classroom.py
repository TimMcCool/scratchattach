import datetime
import requests
from . import user, session
from ..utils.commons import api_iterative, headers
from ..utils import exceptions, commons
from ._base import BaseSiteComponent

class Classroom(BaseSiteComponent):
    def __init__(self, **entries):
        # Info on how the .update method has to fetch the data:
        self.update_function = requests.get
        if "id" in entries:
            self.update_API = f"https://api.scratch.mit.edu/classrooms/{entries['id']}"
        elif "classtoken" in entries:
            self.update_API = f"https://api.scratch.mit.edu/classtoken/{entries['classtoken']}"
        else:
            raise KeyError

        # Set attributes every Project object needs to have:
        self._session = None
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

    def _update_from_dict(self, classrooms):
        try: self.id = int(classrooms["id"])
        except Exception: pass
        try: self.title = classrooms["title"]
        except Exception: pass
        try: self.about_class = classrooms["description"]
        except Exception: pass
        try: self.working_on = classrooms["status"]
        except Exception: pass
        try: self.datetime = datetime.datetime.fromisoformat(classrooms["date_start"])
        except Exception: pass
        try: self.author = user.User(username=classrooms["educator"]["username"],_session=self._session)
        except Exception: pass
        try: self.author._update_from_dict(classrooms["educator"])
        except Exception: pass
        return True
    
    def student_count(self):
        # student count
        text = requests.get(
            f"https://scratch.mit.edu/classes/{self.id}/",
            headers = self._headers
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
        text = requests.get(
            f"https://scratch.mit.edu/classes/{self.id}/students/?page={page}",
            headers = self._headers
        ).text
        textlist = [i.split('/">')[0] for i in text.split('        <a href="/users/')[1:]]
        return textlist
    
    def class_studio_count(self):
        # student count
        text = requests.get(
            f"https://scratch.mit.edu/classes/{self.id}/",
            headers = self._headers
        ).text
        return commons.webscrape_count(text, "Class Studios (", ")")
    
    def class_studio_ids(self, *, page=1):
        """
        Returns the class studio on the class.
        
        Keyword Arguments:
            page: The page of the students that should be returned.
        
        Returns:
            list<str>: The id of the class studios
        """
        text = requests.get(
            f"https://scratch.mit.edu/classes/{self.id}/studios/?page={page}",
            headers = self._headers
        ).text
        textlist = [int(i.split('/">')[0]) for i in text.split('<span class="title">\n    <a href="/studios/')[1:]]
        return textlist



def get_classroom(class_id):
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
    print("Warning: For methods that require authentication, use session.connect_classroom instead of get_classroom")
    return commons._get_object("id", class_id, Classroom, exceptions.ClassroomNotFound)

def get_classroom_from_token(class_token):
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
    print("Warning: For methods that require authentication, use session.connect_classroom instead of get_classroom")
    return commons._get_object("classtoken", class_token, Classroom, exceptions.ClassroomNotFound)