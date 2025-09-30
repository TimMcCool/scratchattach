# classroom alerts (& normal alerts in the future)

from __future__ import annotations

import json
import pprint
import warnings
from dataclasses import dataclass, field, KW_ONLY
from datetime import datetime
from typing_extensions import TYPE_CHECKING, Any, Optional, Union, Self

from . import user, project, studio, comment, session
from scratchattach.utils import enums

if TYPE_CHECKING:
    ...


# todo: implement regular alerts
# If you implement regular alerts, it may be applicable to make EducatorAlert a subclass.


@dataclass
class EducatorAlert:
    """
    Represents an alert for student activity, viewable at https://scratch.mit.edu/site-api/classrooms/alerts/

    Attributes:
        model: The type of alert (presumably); should always equal "educators.educatoralert" in this class
        type: An integer that identifies the type of alert, differentiating e.g. against bans or autoban or censored comments etc
        raw: The raw JSON data from the API
        id: The ID of the alert (internally called 'pk' by scratch, not sure what this is for)
        time_read: The time the alert was read
        time_created: The time the alert was created
        target: The user that the alert is about (the student)
        actor: The user that created the alert (the admin)
        target_object: The object that the alert is about (e.g. a project, studio, or comment)
        notification_type: not sure what this is for, but inferred from the scratch HTML reference
    """
    _: KW_ONLY
    # required attrs
    target: user.User
    actor: user.User
    target_object: Optional[Union[project.Project, studio.Studio, comment.Comment, studio.Studio]]
    notification_type: str
    _session: Optional[session.Session]

    # defaulted attrs
    model: str = "educators.educatoralert"
    type: int = -1
    raw: dict = field(repr=False, default_factory=dict)
    id: int = -1
    time_read: datetime = datetime.fromtimestamp(0.0)
    time_created: datetime = datetime.fromtimestamp(0.0)


    @classmethod
    def from_json(cls, data: dict[str, Any], _session: Optional[session.Session] = None) -> Self:
        """
        Load an EducatorAlert from a JSON object.

        Arguments:
            data (dict): The JSON object
            _session (session.Session): The session object used to load this data, to 'connect' to the alerts rather than just 'get' them

        Returns:
            EducatorAlert: The loaded EducatorAlert object
        """
        model = data.get("model")  # With this class, should be equal to educators.educatoralert
        assert isinstance(model, str)
        alert_id = data.get("pk")  # not sure what kind of pk/id this is. Doesn't seem to be a user or class id.
        assert isinstance(alert_id, int)

        fields = data.get("fields")
        assert isinstance(fields, dict)

        time_read_raw = fields.get("educator_datetime_read")
        assert isinstance(time_read_raw, str)
        time_read: datetime = datetime.fromisoformat(time_read_raw)

        admin_action = fields.get("admin_action")
        assert isinstance(admin_action, dict)

        time_created_raw = admin_action.get("datetime_created")
        assert isinstance(time_created_raw, str)
        time_created: datetime = datetime.fromisoformat(time_created_raw)

        alert_type = admin_action.get("type")
        assert isinstance(alert_type, int)

        target_data = admin_action.get("target_user")
        assert isinstance(target_data, dict)
        target = user.User(username=target_data.get("username"),
                           id=target_data.get("pk"),
                           icon_url=target_data.get("thumbnail_url"),
                           admin=target_data.get("admin", False),
                           _session=_session)

        actor_data = admin_action.get("actor")
        assert isinstance(actor_data, dict)
        actor = user.User(username=actor_data.get("username"),
                          id=actor_data.get("pk"),
                          icon_url=actor_data.get("thumbnail_url"),
                          admin=actor_data.get("admin", False),
                          _session=_session)

        object_id = admin_action.get("object_id")  # this could be a comment id, a project id, etc.
        assert isinstance(object_id, int)
        target_object: project.Project | studio.Studio | comment.Comment | None = None

        extra_data: dict[str, Any] = json.loads(admin_action.get("extra_data", "{}"))
        # todo: if possible, properly implement the incomplete parts of this parser (look for warning.warn())
        notification_type: str = ""

        if "project_title" in extra_data:
            # project
            target_object = project.Project(id=object_id,
                                            title=extra_data["project_title"],
                                            _session=_session)
        elif "comment_content" in extra_data:
            # comment
            comment_data: dict[str, Any] = extra_data["comment_content"]
            content: str | None = comment_data.get("content")

            comment_obj_id: int | None = comment_data.get("comment_obj_id")

            comment_type: int | None = comment_data.get("comment_type")

            if comment_type == 0:
                # project
                comment_source_type = comment.CommentSource.PROJECT
            elif comment_type == 1:
                # profile
                comment_source_type = comment.CommentSource.USER_PROFILE
            else:
                # probably a studio
                comment_source_type = comment.CommentSource.STUDIO
                warnings.warn(
                    f"The parser was not able to recognise the \"comment_type\" of {comment_type} in the alert JSON response.\n"
                    f"Full response: \n{pprint.pformat(data)}.\n\n"
                    f"Please draft an issue on github: https://github.com/TimMcCool/scratchattach/issues, providing this "
                    f"whole error message. This will allow us to implement an incomplete part of this parser")

            # the comment_obj's corresponding attribute of comment.Comment is the place() method. As it has no cache, the title data is wasted.
            # if the comment_obj is deleted, this is still a valid way of working out the title/username

            target_object = comment.Comment(
                id=object_id,
                content=content,
                source=comment_source_type,
                source_id=comment_obj_id,
                _session=_session
            )

        elif "gallery_title" in extra_data:
            # studio
            # possible implemented incorrectly
            target_object = studio.Studio(
                id=object_id,
                title=extra_data["gallery_title"],
                _session=_session
            )
        elif "notification_type" in extra_data:
            # possible implemented incorrectly
            notification_type = extra_data["notification_type"]
        else:
            warnings.warn(
                f"The parser was not able to recognise the \"extra_data\" in the alert JSON response.\n"
                f"Full response: \n{pprint.pformat(data)}.\n\n"
                f"Please draft an issue on github: https://github.com/TimMcCool/scratchattach/issues, providing this "
                f"whole error message. This will allow us to implement an incomplete part of this parser")

        return cls(
            id=alert_id,
            model=model,
            type=alert_type,
            raw=data,
            time_read=time_read,
            time_created=time_created,
            target=target,
            actor=actor,
            target_object=target_object,
            notification_type=notification_type,
            _session=_session
        )

    def __str__(self):
        return f"EducatorAlert: {self.message}"

    @property
    def alert_type(self) -> enums.AlertType:
        """
        Get an associated AlertType object for this alert (based on the type index)
        """
        alert_type = enums.AlertTypes.find(self.type)
        if not alert_type:
            alert_type = enums.AlertTypes.default.value

        return alert_type

    @property
    def message(self):
        """
        Format the alert message using the alert type's message template, as it would be on the website.
        """
        raw_message = self.alert_type.message
        comment_content = ""
        if isinstance(self.target_object, comment.Comment):
            comment_content = self.target_object.content

        return raw_message.format(username=self.target.username,
                                  project=self.target_object_title,
                                  studio=self.target_object_title,
                                  notification_type=self.notification_type,
                                  comment=comment_content)

    @property
    def target_object_title(self):
        """
        Get the title of the target object (if applicable)
        """
        if isinstance(self.target_object, project.Project):
            return self.target_object.title
        if isinstance(self.target_object, studio.Studio):
            return self.target_object.title
        return None  # explicit
