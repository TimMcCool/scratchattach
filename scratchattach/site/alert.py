# classroom alerts (& normal alerts in the future)

from __future__ import annotations

import json
import pprint
import warnings
from dataclasses import dataclass, field, KW_ONLY
from datetime import datetime
from typing import TYPE_CHECKING, Self, Any

from . import user, project, studio, comment, session

if TYPE_CHECKING:
    ...


# todo: implement regular alerts
# If you implement regular alerts, it may be applicable to make EducatorAlert a subclass.


@dataclass
class EducatorAlert:
    _: KW_ONLY
    model: str = "educators.educatoralert"
    type: int = None
    raw: dict = field(repr=False, default=None)
    id: int = None
    time_read: datetime = None
    time_created: datetime = None
    target: user.User = None
    actor: user.User = None
    target_object: project.Project | studio.Studio | comment.Comment = None
    _session: session.Session = None

    @classmethod
    def from_json(cls, data: dict[str, Any], _session: session.Session = None) -> Self:
        model: str = data.get("model")  # With this class, should be equal to educators.educatoralert
        alert_id: int = data.get("pk")  # not sure what kind of pk/id this is. Doesn't seem to be a user or class id.

        fields: dict[str, Any] = data.get("fields")

        # classroom_name = fields.get("classroom_names") # not sure why the JSON key is in plural
        # the classroom name is actually the only direct classroom information provided. however, It can be indirectly worked out using the target user
        time_read: datetime = datetime.fromisoformat(fields.get("educator_datetime_read"))

        admin_action: dict[str, Any] = fields.get("admin_action")

        time_created: datetime = datetime.fromisoformat(admin_action.get("datetime_created"))

        alert_type: int = admin_action.get("type")

        target_data: dict[str, Any] = admin_action.get("target_user")
        target = user.User(username=target_data.get("username"),
                           id=target_data.get("pk"),
                           icon_url=target_data.get("thumbnail_url"),
                           admin=target_data.get("admin", False),
                           _session=_session)

        actor_data: dict[str, Any] = admin_action.get("actor")
        actor = user.User(username=actor_data.get("username"),
                          id=actor_data.get("pk"),
                          icon_url=actor_data.get("thumbnail_url"),
                          admin=actor_data.get("admin", False),
                          _session=_session)

        object_id: int = admin_action.get("object_id")  # this could be a comment id, a project id, etc.
        target_object: project.Project | studio.Studio | comment.Comment | None = None

        extra_data: dict[str, Any] = json.loads(admin_action.get("extra_data", "{}"))
        # todo: properly implement the 2 incomplete parts of this parser (look for warning.warn())

        if "project_title" in extra_data:
            # project
            target_object = project.Project(id=object_id,
                                            title=extra_data["project_title"],
                                            _session=_session)
        elif "comment_content" in extra_data:
            # comment
            comment_data: dict[str, Any] = extra_data["comment_content"]
            content: str | None = comment_data.get("content")
            # comment_id is equal to object_id

            comment_obj_id: int | None = comment_data.get("comment_obj_id")
            # comment_obj_title: str | None = comment_data.get("comment_obj_title")

            # comment_obj: project.Project | studio.Studio | user.User | None = None

            comment_type: int | None = comment_data.get("comment_type")
            # use match case?
            comment_source_type = "Unknown"

            if comment_type == 0:
                # project
                comment_source_type = "project"
                # comment_obj = project.Project(id=comment_obj_id,
                #                               title=comment_obj_title,
                #                               _session=_session)
            elif comment_type == 1:
                # profile
                comment_source_type = "profile"
                # comment_obj = user.User(id=comment_obj_id,
                #                         username=comment_obj_title, # yes, it's called title, but it can store a username too
                #                         _session=_session)
            else:
                # probably a studio
                warnings.warn(
                    f"The parser was not able to recognise the \"comment_type\" of {comment_type} in the alert JSON response.\n"
                    f"Full response: \n{pprint.pformat(data)}.\n\n"
                    f"Please draft an issue on github: https://github.com/TimMcCool/scratchattach/issues, providing this "
                    f"whole error message. This will allow us to implement an incomplete part of this parser")

                # theoretical parser. might now work
                comment_source_type = "studio"
                # comment_obj = studio.Studio(id=comment_obj_id,
                #                             title=comment_obj_title,
                #                             _session=_session)

            # the comment_obj's corresponding attribute of comment.Comment is the place() method. As it has no cache, the title data is wasted.
            # if the comment_obj is deleted, this is still a valid way of working out the title/username

            target_object = comment.Comment(
                id=object_id,
                content=content,
                source=comment_source_type,
                source_id=comment_obj_id,
                _session=_session
            )
        else:
            # probably a studio
            # possibly forums? Profile?
            warnings.warn(
                f"The parser was not able to recognise the \"extra_data\" in the alert JSON response.\n"
                f"Full response: \n{pprint.pformat(data)}.\n\n"
                f"Please draft an issue on github: https://github.com/TimMcCool/scratchattach/issues, providing this "
                f"whole error message. This will allow us to implement an incomplete part of this parser")

            # theoretical parser. might now work
            # also, what if it's a profile?
            target_object = studio.Studio(
                id=object_id,
                title=extra_data.get("gallery_title"),  # i have no idea if this is the correct key
                _session=_session
            )

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
            _session=_session
        )
