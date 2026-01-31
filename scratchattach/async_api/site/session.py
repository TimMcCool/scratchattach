import warnings
import httpx
import re
import contextlib

from datetime import datetime
from dataclasses import KW_ONLY, dataclass, field
from typing_extensions import Any, AsyncContextManager, Optional, Self, cast

from scratchattach.utils import commons, exceptions, typed_dicts


@dataclass
class Session:
    _: KW_ONLY
    id: str = field(repr=False)
    rq: httpx.AsyncClient = field(repr=False)
    user_id: int
    username: str
    xtoken: str = field(repr=False)
    created_at: datetime

    # the following attributes are set in the `update()` function.
    has_outstanding_email_confirmation: Optional[bool] = None
    email: Optional[str] = field(repr=False, default=None)
    is_new_scratcher: Optional[bool] = None
    is_teacher: Optional[bool] = None
    is_teacher_invitee: Optional[bool] = None
    mute_status: Optional[dict | typed_dicts.SessionOffensesDict] = None
    is_banned: Optional[bool] = None

    def __post_init__(self):
        self.rq.headers["X-Token"] = self.xtoken
        self.rq.cookies.update(
            {
                "scratchsessionsid": self.id,
                "scratchcsrftoken": "a",
                "scratchlanguage": "en",
                "accept": "application/json",
                "Content-Type": "application/json",
            }
        )

    def __str__(self) -> str:
        return f"-L {self.username}"

    async def update(self):
        # I don't really see the point of abstracting the update url and stuff
        resp = await self.rq.post("https://scratch.mit.edu/session")
        data = cast(typed_dicts.SessionDict, resp.json())
        self.has_outstanding_email_confirmation = data["flags"]["has_outstanding_email_confirmation"]

        self.email = data["user"]["email"]

        self.is_new_scratcher = data["permissions"]["new_scratcher"]
        self.is_teacher = data["permissions"]["educator"]
        self.is_teacher_invitee = data["permissions"]["educator_invitee"]

        self.mute_status = data["permissions"]["mute_status"]

        self.username = data["user"]["username"]
        self.banned = data["user"]["banned"]

        if self.xtoken != data["user"]["token"]:
            warnings.warn(f"Differing xtoken {data['user']['token']!r}")
        if self.banned:
            warnings.warn(
                f"Warning: The account {self.username} you logged in to is BANNED. Some features may not work properly."
            )
        if self.has_outstanding_email_confirmation:
            warnings.warn(
                f"Warning: The account {self.username} you logged is not email confirmed. Some features may not work properly."
            )


@contextlib.asynccontextmanager
async def _build_session(*, id: str, rq: httpx.AsyncClient, username: Optional[str]):
    try:
        data, created_at = commons.decode_session_id(id)
        assert data["username"] == username or username is None
        # not saving the login ip because it can be considered as a security issue, and is not very helpful
        yield Session(
            id=id,
            rq=rq,
            created_at=created_at,
            username=data["username"],
            user_id=int(data["_auth_user_id"]),
            xtoken=data["token"],
        )
    finally:
        pass


def _make_rq(kwargs: Optional[dict[str, Any]]) -> httpx.AsyncClient:
    if kwargs is None:
        kwargs = {}
    return httpx.AsyncClient(
        follow_redirects=True, headers=commons.headers | {"Cookie": "scratchcsrftoken=a;scratchlanguage=en;"}, **kwargs
    )


async def login(
    username: str, password: str, *, client_args: Optional[dict[str, Any]] = None
) -> AsyncContextManager[Session, bool | None]:
    if client_args is None:
        client_args = {}

    print("TODO: issue_login_warning")
    rq = _make_rq(client_args)
    resp = await rq.post("https://scratch.mit.edu/login/", json={"username": username, "password": password})
    if not (match := re.search('"(.*)"', resp.headers.get("Set-Cookie", ""))):
        raise exceptions.LoginFailure(
            "Either the provided authentication data is wrong or your network is banned from Scratch.\n\nIf you're using an online IDE (like replit.com) Scratch possibly banned its IP address. In this case, try logging in with your session id: https://github.com/TimMcCool/scratchattach/wiki#logging-in"
        )

    session_id = match.group()

    return await login_by_id(session_id, rq=rq)


async def login_by_id(
    session_id: str,
    *,
    username: Optional[str] = None,
    rq: Optional[httpx.AsyncClient] = None,
    client_args: Optional[dict[str, Any]] = None,
) -> AsyncContextManager[Session, bool | None]:
    if rq is None:
        rq = _make_rq(client_args)
    print("TODO: issue_login_warning")

    return _build_session(id=session_id, rq=rq, username=username)
