from __future__ import annotations

from typing import TypedDict, Union

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
    pass

class SessionDict(TypedDict):
    user: SessionUserDict
    permissions: SessionPermissionsDict
    flags: SessionFlagsDict