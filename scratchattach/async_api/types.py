from typing import Optional
from typing_extensions import TypedDict, Literal, NotRequired, Union

SessionIDDict = TypedDict(
    "SessionIDDict",
    {
        "username": str,
        "_auth_user_id": str,
        "testcookie": Literal["worked"],
        "_auth_user_backend": Literal["authentication.backends.ReplicationBackend"],
        "token": str,
        "login-ip": str,
        "_language": str,  #'en'
        "django_timezone": Literal["America/New_York"],
        "_auth_user_hash": str,
    },
)


class SessionUserDict(TypedDict):
    id: int
    banned: bool
    should_vpn: bool
    username: str
    token: str
    thumbnailUrl: str
    dateJoined: str
    email: str
    birthYear: int
    birthMonth: int
    gender: str
    state: str | None  # for USA; TODO: consider making some kind of enum for this
    membership_avatar_badge: bool | None  # i think this is the type
    membership_label: bool | None  # i think this is the type


class SessionOffenseDict(TypedDict):
    expiresAt: float
    messageType: str
    createdAt: float


class SessionOffensesDict(TypedDict):
    offenses: list[SessionOffenseDict]
    showWarning: bool
    muteExpiresAt: float
    currentMessageType: str


class SessionPermissionsDict(TypedDict):
    admin: bool
    scratcher: bool
    new_scratcher: bool
    invited_scratcher: bool
    social: bool
    educator: bool
    educator_invitee: bool
    student: bool
    mute_status: Union[dict, SessionOffensesDict]


class SessionFlagsDict(TypedDict):
    must_reset_password: bool
    must_complete_registration: bool
    has_outstanding_email_confirmation: bool
    show_welcome: bool
    confirm_email_banner: bool
    unsupported_browser_banner: bool
    with_parent_email: bool
    project_comments_enabled: bool
    gallery_comments_enabled: bool
    userprofile_comments_enabled: bool
    everything_is_totally_normal: bool


class SessionDict(TypedDict):
    user: NotRequired[SessionUserDict]
    permissions: NotRequired[SessionPermissionsDict]
    flags: SessionFlagsDict
