"""Comment class"""
from __future__ import annotations

import warnings
import html

from dataclasses import dataclass
from typing_extensions import assert_never
from typing import Union, Optional, Any
from enum import Enum, auto

from . import user, project, studio, session
from ._base import BaseSiteComponent
from scratchattach.utils import exceptions

class CommentSource(Enum):
    PROJECT = auto()
    USER_PROFILE = auto()
    STUDIO = auto()
    UNKNOWN = auto()

@dataclass
class Comment(BaseSiteComponent):
    """
    Represents a Scratch comment (on a profile, studio or project)
    """
    id: Optional[int | str] = None
    source: CommentSource = CommentSource.UNKNOWN
    source_id: Optional[int | str] = None
    cached_replies: Optional[list[Comment]] = None
    parent_id: Optional[int | str] = None
    cached_parent_comment: Optional[Comment] = None
    commentee_id: Optional[int] = None
    content: Optional[str] = None
    reply_count: Optional[int] = None
    written_by_scratchteam: Optional[bool] = None
    author_id: Optional[int] = None
    author_name: Optional[str] = None

    _session: Optional[session.Session] = None

    def __str__(self):
        return self.text

    def update(self):
        warnings.warn("Warning: Comment objects can't be updated")
        return False  # Objects of this type cannot be updated

    def _update_from_dict(self, data: dict[str, str | dict | Any]):
        self.id = data["id"]
        self.parent_id = data.get("parent_id")
        self.commentee_id = data.get("commentee_id")
        self.content = str(data["content"])
        self.datetime_created = data["datetime_created"]

        author = data.get("author", {})
        self.author_name = author.get("username", self.author_name)
        self.author_id = author.get("id", self.author_id)
        self.written_by_scratchteam = author.get("scratchteam", self.written_by_scratchteam)
        self.reply_count = data.get("reply_count", self.reply_count)

        source: str = data.get("source")
        if self.source is CommentSource.UNKNOWN:
            self.source = {
                "project": CommentSource.PROJECT,
                "studio": CommentSource.STUDIO,
                "profile": CommentSource.USER_PROFILE,
                None: CommentSource.UNKNOWN,
            }[source]

        self.source_id = data.get("source_id", self.source_id)

    @property
    def text(self) -> str:
        """
        Parsed version of Comment.content. This removes any escape codes, e.g. '&apos;' becomes ', an apostrophe
        """
        if self.source is CommentSource.USER_PROFILE:
            # user profile comments do not seem to be escaped
            return self.content

        return str(html.unescape(self.content))

    # Methods for getting related entities

    def author(self) -> user.User:
        return self._make_linked_object("username", self.author_name, user.User, exceptions.UserNotFound)

    def place(self) -> user.User | studio.Studio | project.Project:
        """
        Returns the place (the project, profile or studio) where the comment was posted as Project, User, or Studio object.

        If the place can't be traced back, None is returned.
        """
        if self.source == CommentSource.USER_PROFILE:
            return self._make_linked_object("username", self.source_id, user.User, exceptions.UserNotFound)
        elif self.source == CommentSource.STUDIO:
            return self._make_linked_object("id", self.source_id, studio.Studio, exceptions.UserNotFound)
        elif self.source == CommentSource.PROJECT:
            return self._make_linked_object("id", self.source_id, project.Project, exceptions.UserNotFound)
        else:
            assert_never(self.source)

    def parent_comment(self) -> Comment | None:
        if self.parent_id is None:
            return None

        if self.cached_parent_comment is not None:
            return self.cached_parent_comment

        if self.source == "profile":
            self.cached_parent_comment = user.User(username=self.source_id, _session=self._session).comment_by_id(
                self.parent_id)

        elif self.source == "project":
            p = project.Project(id=self.source_id, _session=self._session)
            p.update()
            self.cached_parent_comment = p.comment_by_id(self.parent_id)

        elif self.source == "studio":
            self.cached_parent_comment = studio.Studio(id=self.source_id, _session=self._session).comment_by_id(
                self.parent_id)

        return self.cached_parent_comment

    def replies(self, *, use_cache: bool = True, limit=40, offset=0):
        """
        Keyword Arguments:
            use_cache (bool): Returns the replies cached on the first reply fetch. This makes it SIGNIFICANTLY faster for profile comments. Warning: For profile comments, the replies are retrieved and cached on object creation.
        """
        if (self.cached_replies is None) or (not use_cache):
            if self.source == CommentSource.USER_PROFILE:
                self.cached_replies = user.User(username=self.source_id, _session=self._session).comment_by_id(
                    self.id).cached_replies[offset:offset + limit]

            elif self.source == CommentSource.PROJECT:
                p = project.Project(id=self.source_id, _session=self._session)
                p.update()
                self.cached_replies = p.comment_replies(comment_id=self.id, limit=limit, offset=offset)

            elif self.source == CommentSource.STUDIO:
                self.cached_replies = studio.Studio(id=self.source_id, _session=self._session).comment_replies(
                    comment_id=self.id, limit=limit, offset=offset)

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
            :param content: Content of the comment to send
            :param commentee_id: ID of user to reply to
        """

        self._assert_auth()
        parent_id = str(self.id)
        if self.parent_id is not None:
            parent_id = str(self.parent_id)
        if commentee_id is None:
            if self.author_id:
                commentee_id = self.author_id
            else:
                commentee_id = ""

        if self.source == CommentSource.USER_PROFILE:
            return user.User(username=self.source_id, _session=self._session).reply_comment(content,
                                                                                            parent_id=str(parent_id),
                                                                                            commentee_id=commentee_id)
        if self.source == CommentSource.PROJECT:
            p = project.Project(id=self.source_id, _session=self._session)
            p.update()
            return p.reply_comment(content, parent_id=str(parent_id), commentee_id=commentee_id)

        if self.source == CommentSource.STUDIO:
            return studio.Studio(id=self.source_id, _session=self._session).reply_comment(content,
                                                                                          parent_id=str(parent_id),
                                                                                          commentee_id=commentee_id)
        raise ValueError(f"Unknown source: {self.source}")

    def delete(self):
        """
        Deletes the comment.
        """
        self._assert_auth()
        if self.source == CommentSource.USER_PROFILE:
            return user.User(username=self.source_id, _session=self._session).delete_comment(comment_id=self.id)

        elif self.source == CommentSource.PROJECT:
            p = project.Project(id=self.source_id, _session=self._session)
            p.update()
            return p.delete_comment(comment_id=self.id)

        elif self.source == CommentSource.STUDIO:
            return studio.Studio(id=self.source_id, _session=self._session).delete_comment(comment_id=self.id)
        
        return None  # raise error?

    def report(self):
        """
        Reports the comment to the Scratch team.
        """
        self._assert_auth()
        if self.source == CommentSource.USER_PROFILE:
            user.User(username=self.source_id, _session=self._session).report_comment(comment_id=self.id)

        elif self.source == CommentSource.PROJECT:
            p = project.Project(id=self.source_id, _session=self._session)
            p.update()
            p.report_comment(comment_id=self.id)

        elif self.source == CommentSource.STUDIO:
            studio.Studio(id=self.source_id, _session=self._session).report_comment(comment_id=self.id)
