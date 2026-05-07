import base64
import datetime
import dataclasses
import httpx
import json
import zlib

from typing_extensions import Optional

from scratchattach.async_api import commons, err, types


@dataclasses.dataclass
class Session:
    # this is the *only* required attribute!
    # all other attributes can be `None` if they have not been set yet.
    # they act as a cache. If you want to guarantee output, use the
    # associated getter functions instead.
    # There's little point in using @property for this because we are async
    # anyway, and any verboseness reduction as a tradeoff for clarity is lost
    # since you need to `await` it anyway. so we might as well provide clarity.
    client: httpx.AsyncClient

    _username: Optional[str] = None
    _user_id: Optional[int] = None
    _xtoken: Optional[str] = None
    _login_ip: Optional[str] = None
    _created_at: Optional[datetime.datetime] = None

    _is_banned: Optional[bool] = None
    _should_vpn: Optional[bool] = None
    _joined_at: Optional[datetime.datetime] = None
    _email: Optional[str] = None
    # not datetime.date as that could be misleading as there is no 'day' field
    _birthyear: Optional[int] = None
    _birthmonth: Optional[int] = None
    _gender: Optional[str] = None
    _state: Optional[str] = None

    # TODO: it would be ideal to actually parse these into their own dataclasses
    # _flags: Optional[types.SessionFlagsDict] = None
    # _permissions: Optional[types.SessionPermissionsDict] = None

    # TODO: membership booleans

    def __repr__(self) -> str:
        return "-L async session"

    def get_session_id(self) -> str:
        sessid = self.client.cookies.get("scratchsessionsid")
        if sessid is None:
            raise err.AuthenticationError("No session id")

        return sessid

    def update_from_session_id(self):
        sessid = self.get_session_id()
        data, timestamp = decode_session_id(sessid)

        self._username = data["username"]
        self._user_id = int(data["_auth_user_id"])
        self._xtoken = data["token"]
        self._login_ip = data["login-ip"]
        self._created_at = timestamp

    async def update(self):
        resp = await self.client.get("https://scratch.mit.edu/session/")
        resp.raise_for_status()

        data: types.SessionDict = resp.json()
        user = data.get("user")
        if user is None:
            raise err.AuthenticationError("Could not retrieve the associated user for the session. Is your session id valid?")

        self._user_id = user["id"]
        self._is_banned = user["banned"]
        self._should_vpn = user["should_vpn"]
        self._username = user["username"]
        self._xtoken = user["token"]
        # skipping thumbnailurl as it can be inferred from userid
        # TODO: consider making functions to convert thumbnail urls to ids
        self._joined_at = datetime.datetime.fromisoformat(user["dateJoined"])
        self._email = user["email"]
        self._birthyear = user["birthYear"]
        self._birthmonth = user["birthMonth"]
        self._gender = user["gender"]
        self._state = user["state"]


def _make_default_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        timeout=10, headers=commons.HEADERS.copy(), cookies={"scratchcsrftoken": "a", "scratchlanguage": "en"}
    )


async def login_by_id(session_id: str, *, client: Optional[httpx.AsyncClient] = None) -> Session:
    if client is None:
        client = _make_default_client()

    client.cookies.set("scratchsessionsid", session_id)

    sess = Session(client)
    sess.update_from_session_id()
    await sess.update()
    return sess


async def login(username: str, password: str, *, client: Optional[httpx.AsyncClient] = None) -> Session:
    if client is None:
        client = _make_default_client()

    resp = await client.post("https://scratch.mit.edu/login/", json={"username": username, "password": password})
    sessid = resp.cookies.get("scratchsessionsid")
    if sessid is None:
        raise err.AuthenticationError(
            "Either the provided username/password is invalid or your network is banned from scratch. "
            "If you are using an online IDE like https://repl.it, scratch may have banned its IP address"
        )

    return await login_by_id(sessid, client=client)


# TODO: TypedDict
def decode_session_id(session_id: str) -> tuple[types.SessionIDDict, datetime.datetime]:
    p1, p2, _ = session_id.split(":")
    p1_bytes = base64.urlsafe_b64decode(p1 + "==")
    if p1.startswith('".'):
        p1_bytes = zlib.decompress(p1_bytes)

    return (json.loads(p1_bytes), datetime.datetime.fromtimestamp(commons.b62_decode(p2)))
