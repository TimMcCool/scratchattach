import httpx
import re
import contextlib

from datetime import datetime
from dataclasses import KW_ONLY, dataclass, field
from typing_extensions import Any, AsyncContextManager, Optional, Self

from scratchattach.utils import commons, exceptions


@dataclass
class Session:
    _: KW_ONLY
    id: str = field(repr=False)
    rq: httpx.AsyncClient = field(repr=False)
    user_id: int
    username: str
    xtoken: str
    created_at: datetime

    def __post_init__(self):
        self.rq.headers["X-Token"] = self.xtoken


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


async def login(
    username: str, password: str, *, client_args: Optional[dict[str, Any]] = None
) -> AsyncContextManager[Session, bool | None]:
    if client_args is None:
        client_args = {}

    print("TODO: issue_login_warning")
    rq = httpx.AsyncClient(
        headers=commons.headers.copy() | {"Cookie": "scratchcsrftoken=a;scratchlanguage=en;"}, **client_args
    )
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
    if client_args is None:
        client_args = {}
    if rq is None:
        rq = httpx.AsyncClient(headers=commons.headers.copy(), **client_args)
    print("TODO: issue_login_warning")

    return _build_session(id=session_id, rq=rq, username=username)
