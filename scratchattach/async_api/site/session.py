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

        data = resp.json()
        if "user" not in data:
            raise err.AuthenticationError("Could not retrieve the associated user for the session. Is your session id valid?")

        print(f"Session.update, {data=}")


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
