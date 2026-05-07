import httpx
import dataclasses

from typing_extensions import Optional

from scratchattach.async_api import commons


@dataclasses.dataclass
class Session:
    client: httpx.AsyncClient

    async def update(self):
        resp = await self.client.get("https://scratch.mit.edu/session/")
        resp.raise_for_status()

        data = resp.json()
        if "user" not in data:
            raise AuthenticationError("Could not retrieve the associated user for the session. Is your session id valid?")

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
    await sess.update()
    return sess


async def login(username: str, password: str, *, client: Optional[httpx.AsyncClient] = None) -> Session:
    if client is None:
        client = _make_default_client()

    resp = await client.post("https://scratch.mit.edu/login/", json={"username": username, "password": password})
    sessid = resp.cookies.get("scratchsessionsid")
    if sessid is None:
        raise AuthenticationError(
            "Either the provided username/password is invalid or your network is banned from scratch. "
            "If you are using an online IDE like https://repl.it, scratch may have banned its IP address"
        )

    return await login_by_id(sessid, client=client)


class AuthenticationError(Exception):
    pass
