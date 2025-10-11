from __future__ import annotations

from typing_extensions import OrderedDict

from scratchattach.cloud import _base
from typing import TypedDict, Union, Optional, Required, NotRequired

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
    user: SessionUserDict
    permissions: SessionPermissionsDict
    flags: SessionFlagsDict

class UserHistoryDict(TypedDict):
    joined: str

class UserProfileDict(TypedDict):
    id: int
    status: str
    bio: str
    country: str
    images: dict[str, str]

class UserDict(TypedDict):
    id: NotRequired[int]
    username: NotRequired[str]
    scratchteam: NotRequired[bool]
    history: NotRequired[UserHistoryDict]
    profile: NotRequired[UserProfileDict]

class CloudLogActivityDict(TypedDict):
    user: str
    verb: str
    name: str
    value: Union[str, float, int]
    timestamp: int
    cloud: _base.AnyCloud

class CloudActivityDict(TypedDict):
    method: str
    name: str
    value: Union[str, float, int]
    project_id: int
    cloud: _base.AnyCloud

class ClassroomDict(TypedDict):
    id: int
    title: str
    description: str
    status: str
    date_start: NotRequired[str]
    date_end: NotRequired[Optional[str]]
    images: NotRequired[dict[str, str]]
    educator: UserDict
    is_closed: NotRequired[bool]

class StudioHistoryDict(TypedDict):
    created: str
    modified: str

class StudioStatsDict(TypedDict):
    followers: int
    managers: int
    projects: int

class StudioDict(TypedDict):
    id: int
    title: str
    description: str
    host: int
    open_to_all: bool
    comments_allowed: bool
    image: str
    history: StudioHistoryDict
    stats: NotRequired[StudioStatsDict]

class StudioRoleDict(TypedDict):
    manager: bool
    curator: bool
    invited: bool
    following: bool

class PlaceholderProjectDataMetadataDict(TypedDict):
    title: str
    description: str

# https://github.com/GarboMuffin/placeholder/blob/e1e98953342a40abbd626a111f621711f74e783b/src/routes/projects/%5Bproject%5D/%2Bpage.server.ts#L19
class PlaceholderProjectDataDict(TypedDict):
    metadata: PlaceholderProjectDataMetadataDict
    md5extsToSha256: OrderedDict[str, str]
    adminOwnershipToken: Optional[str]
