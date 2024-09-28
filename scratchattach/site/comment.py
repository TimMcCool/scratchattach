"""v2 ready: Comment class"""

import json
import re

from ..utils import commons

from . import user
from . import session
from . import project
from . import studio
from . import forum
from ..utils import exceptions
from ._base import BaseSiteComponent
from ..utils.commons import headers
from bs4 import BeautifulSoup

from ..utils.requests import Requests as requests

class Comment(BaseSiteComponent):

    '''
    Represents a Scratch comment (on a profile, studio or project)
    '''

    def str(self):
        return str(self.content)

    def __init__(self, **entries):

        # Set attributes every Comment object needs to have:
        self.id = None
        self._session = None
        self.source=None
        self.source_id = None
        self.cached_replies = None
        self.parent_id = None
        self.cached_parent_comment = None
        if not "source" in entries:
            "source" == "Unknown"

        # Update attributes from entries dict:
        self.__dict__.update(entries)

    def update(self):
        # comments can't be updated
        pass

    def _update_from_dict(self, data):
        try: self.id = data["id"]
        except Exception: pass
        try: self.parent_id = data["parent_id"]
        except Exception: pass
        try: self.commentee_id = data["commentee_id"]
        except Exception: pass
        try: self.content = data["content"]
        except Exception: pass
        try: self.datetime_created = data["datetime_created"]
        except Exception: pass
        try: self.author_name = data["author"]["username"]
        except Exception: pass
        try: self.author_id = data["author"]["id"]
        except Exception: pass
        try: self.written_by_scratchteam = data["author"]["scratchteam"]
        except Exception: pass
        try: self.reply_count = data["reply_count"]
        except Exception: pass
        try: self.source = data["source"]
        except Exception: pass
        try: self.source_id = data["source_id"]
        except Exception: pass
        return True

    # Methods for getting related entities

    def author(self):
        return self._make_linked_object("username", self.author_name, user.User, exceptions.UserNotFound)

    def place(self):
        """
        Returns the place (the project, profile or studio) where the comment was posted as Project, User, or Studio object.

        If the place can't be traced back, None is returned.
        """
        if self.source == "profile":
            return self._make_linked_object("username", self.source_id, user.User, exceptions.UserNotFound)
        if self.source == "studio":
            return self._make_linked_object("id", self.source_id, studio.Studio, exceptions.UserNotFound)
        if self.source == "project":
            return self._make_linked_object("id", self.source_id, project.Project, exceptions.UserNotFound)

    def parent_comment(self):
        if self.parent_id is None:
            return None
        if self.cached_parent_comment is not None:
            return self.cached_parent_comment
        if self.source == "profile":
            self.cached_parent_comment = user.User(username=self.source_id, _session=self._session).comment_by_id(self.parent_id)
        if self.source == "project":
            p = project.Project(id=self.source_id, _session=self._session)
            p.update()
            self.cached_parent_comment = p.comment_by_id(self.parent_id)
        if self.source == "studio":
            self.cached_parent_comment = studio.Studio(id=self.source_id, _session=self._session).comment_by_id(self.parent_id)
        return self.cached_parent_comment
    
    def replies(self, *, use_cache=True, limit=40, offset=0):
        """
        Keyword Arguments:
            use_cache (bool): Returns the replies cached on the first reply fetch. This makes it SIGNIFICANTLY faster for profile comments. Warning: For profile comments, the replies are retrieved and cached on object creation.
        """
        if (self.cached_replies is None) or (use_cache is False):
            if self.source == "profile":
                self.cached_replies = user.User(username=self.source_id, _session=self._session).comment_by_id(self.id).cached_replies[offset:offset+limit]
            if self.source == "project":
                p = project.Project(id=self.source_id, _session=self._session)
                p.update()
                self.cached_replies = p.comment_replies(comment_id=self.id, limit=limit, offset=offset)
            if self.source == "studio":
                self.cached_replies = studio.Studio(id=self.source_id, _session=self._session).comment_replies(comment_id=self.id, limit=limit, offset=offset)
        return self.cached_replies
    
    # Methods for dealing with the comment

    def reply(self, content, *, commentee_id=None):
        """
        Posts a reply comment to the comment.
        
        Warning:
            Scratch only shows comments replying to top-level comments, and all replies to replies are actually replies to top-level comments in the API.

            Therefore, if this comment is a reply, this method will not reply to the comment itself but to the corresponding top-level comment.
    
        Args:
            content (str): Comment content to post.

        Keyword args:
            commentee_id (None or str): If set to None (default), it will automatically fill out the commentee ID with the user ID of the parent comment author. Set it to "" to mention no user.


        Returns:
            scratchattach.Comment: The created comment.
        """

        self._assert_auth()
        parent_id = str(self.id)
        if self.parent_id is not None:
            parent_id = str(self.parent_id)
        if commentee_id is None:
            if "author_id" in self.__dict__:
                commentee_id = self.author_id
            else:
                commentee_id = ""
        if self.source == "profile":
            return user.User(username=self.source_id, _session=self._session).reply_comment(content, parent_id=str(parent_id), commentee_id=commentee_id)
        if self.source == "project":
            p = project.Project(id=self.source_id, _session=self._session)
            p.update()
            return p.reply_comment(content, parent_id=str(parent_id), commentee_id=commentee_id)
        if self.source == "studio":
            return studio.Studio(id=self.source_id, _session=self._session).reply_comment(content, parent_id=str(parent_id), commentee_id=commentee_id)


    def delete(self):
        """
        Deletes the comment.
        """
        self._assert_auth()
        if self.source == "profile":
            user.User(username=self.source_id, _session=self._session).delete_comment(comment_id=self.id)
        if self.source == "project":
            p = project.Project(id=self.source_id, _session=self._session)
            p.update()
            p.delete_comment(comment_id=self.id)
        if self.source == "studio":
            studio.Studio(id=self.source_id, _session=self._session).delete_comment(comment_id=self.id)

    def report(self):
        """
        Reports the comment to the Scratch team.
        """
        self._assert_auth()
        if self.source == "profile":
            user.User(username=self.source_id, _session=self._session).report_comment(comment_id=self.id)
        if self.source == "project":
            p = project.Project(id=self.source_id, _session=self._session)
            p.update()
            p.report_comment(comment_id=self.id)
        if self.source == "studio":
            studio.Studio(id=self.source_id, _session=self._session).report_comment(comment_id=self.id)