from __future__ import annotations

from collections.abc import MutableMapping, Iterator
from abc import ABC, abstractmethod
from types import TracebackType
from typing import Optional, Any, Self, Union
from contextlib import contextmanager
from enum import Enum, auto
from dataclasses import dataclass, field
import json

from aiohttp.cookiejar import DummyCookieJar
from typing_extensions import override
from requests import Session as HTTPSession
from requests import Response
import aiohttp

from . import exceptions
from . import optional_async

proxies: Optional[MutableMapping[str, str]] = None

class HTTPMethod(Enum):
    GET = auto()
    POST = auto()
    PUT = auto()
    DELETE = auto()
    HEAD = auto()
    OPTIONS = auto()
    PATCH = auto()
    TRACE = auto()
    @classmethod
    def of(cls, name: str) -> HTTPMethod:
        member_map = {
            "GET": cls.GET,
            "POST": cls.POST,
            "PUT": cls.PUT,
            "DELETE": cls.DELETE,
            "HEAD": cls.HEAD,
            "OPTIONS": cls.OPTIONS,
            "PATCH": cls.PATCH,
            "TRACE": cls.TRACE
        }
        return member_map[name]

class AnyHTTPResponse(ABC):
    request_method: HTTPMethod
    status_code: int
    content: bytes
    text: str
    headers: dict[str, str]
    
    def json(self) -> Any:
        return json.loads(self.text)

@dataclass
class HTTPResponse(AnyHTTPResponse):
    request_method: HTTPMethod = field(kw_only=True)
    status_code: int = field(kw_only=True)
    content: bytes = field(kw_only=True)
    text: str = field(kw_only=True)
    headers: dict[str, str] = field(kw_only=True)

class OAHTTPSession(ABC):
    error_handling: bool = True
    @abstractmethod
    def sync_request(
        self,
        method: HTTPMethod,
        url: str,
        *,
        cookies: Optional[dict[str, str]] = None,
        headers: Optional[dict[str, str]] = None,
        params: Optional[dict[str, str]] = None,
        data: Optional[Union[dict[str, str], str]] = None,
        json: Optional[Any] = None
    ) -> AnyHTTPResponse:
        pass
    
    @abstractmethod
    async def async_request(
        self,
        method: HTTPMethod,
        url: str,
        *,
        cookies: Optional[dict[str, str]] = None,
        headers: Optional[dict[str, str]] = None,
        params: Optional[dict[str, str]] = None,
        data: Optional[Union[dict[str, str], str]] = None,
        json: Optional[Any] = None
    ) -> AnyHTTPResponse:
        pass

    def check_response(self, r: AnyHTTPResponse):
        if r.status_code == 403 or r.status_code == 401:
            raise exceptions.Unauthorized(f"Request content: {r.content!r}")
        if r.status_code == 500:
            raise exceptions.APIError("Internal Scratch server error")
        if r.status_code == 429:
            raise exceptions.Response429("You are being rate-limited (or blocked) by Scratch")
        if r.json() == {"code":"BadRequest","message":""}:
            raise exceptions.BadRequest("Make sure all provided arguments are valid")
    
    
    def request(
        self,
        method: Union[HTTPMethod, str],
        url: str,
        *,
        cookies: Optional[dict[str, str]] = None,
        headers: Optional[dict[str, str]] = None,
        params: Optional[dict[str, str]] = None,
        data: Optional[Union[dict[str, str], str]] = None,
        json: Optional[Any] = None
    ) -> optional_async.CARequest:
        if isinstance(method, str):
            method = HTTPMethod.of(method.upper())
        return optional_async.CARequest(
            self,
            method,
            url,
            cookies = cookies,
            headers = headers,
            params = params,
            data = data,
            json = json
        )
    
    @contextmanager
    def no_error_handling(self) -> Iterator[None]:
        val_before = self.error_handling
        self.error_handling = False
        try:
            yield
        finally:
            self.error_handling = val_before
    
    @contextmanager
    def yes_error_handling(self) -> Iterator[None]:
        val_before = self.error_handling
        self.error_handling = True
        try:
            yield
        finally:
            self.error_handling = val_before

class SyncRequests(OAHTTPSession):
    @override
    def sync_request(self, method, url, *, cookies = None, headers = None, params = None, data = None, json = None):
        try:
            r = requests.request(
                method.name,
                url,
                cookies = cookies,
                headers = headers,
                params = params,
                data = data,
                json = json,
                proxies = proxies
            )
        except Exception as e:
            raise exceptions.FetchError(e)
        response = HTTPResponse(
            request_method=method,
            status_code=r.status_code,
            content=r.content,
            text=r.text,
            headers=r.headers
        )
        if self.error_handling:
            self.check_response(response)
        return response
    
    async def async_request(self, method, url, *, cookies = None, headers = None, params = None, data = None, json = None):
        raise NotImplementedError()

class AsyncRequests(OAHTTPSession):
    client_session: aiohttp.ClientSession
    async def __aenter__(self) -> Self:
        self.client_session = await aiohttp.ClientSession(cookie_jar=DummyCookieJar()).__aenter__()
        return self
    
    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]] = None,
        exc_val: Optional[BaseException] = None,
        exc_tb: Optional[TracebackType] = None
    ) -> None:
        await self.client_session.__aexit__(exc_type, exc_val, exc_tb)
    
    @override
    def sync_request(self, method, url, *, cookies = None, headers = None, params = None, data = None, json = None):
        raise NotImplementedError()
    
    async def async_request(self, method, url, *, cookies = None, headers = None, params = None, data = None, json = None):
        proxy = None
        if url.startswith("http"):
            proxy = proxies.get("http")
        if url.startswith("https"):
            proxy = proxies.get("https")
        async with self.client_session.request(
            method.name,
            url,
            cookies = cookies,
            headers = headers,
            params = params,
            data = data,
            json = json,
            proxy = proxy
        ) as resp:
            assert isinstance(resp, aiohttp.ClientResponse)
            content = await resp.read()
            try:
                text = content.decode(resp.get_encoding())
            except Exception:
                text = ""
            response = HTTPResponse(
                request_method=method,
                status_code=resp.status,
                content=content,
                text=text,
                headers=resp.headers
            )
            if self.error_handling:
                self.check_response(response)
            return response

class Requests(HTTPSession):
    """
    Centralized HTTP request handler (for better error handling and proxies)
    """
    error_handling: bool = True

    def check_response(self, r: Response):
        if r.status_code == 403 or r.status_code == 401:
            raise exceptions.Unauthorized(f"Request content: {r.content!r}")
        if r.status_code == 500:
            raise exceptions.APIError("Internal Scratch server error")
        if r.status_code == 429:
            raise exceptions.Response429("You are being rate-limited (or blocked) by Scratch")
        if r.json() == {"code":"BadRequest","message":""}:
            raise exceptions.BadRequest("Make sure all provided arguments are valid")

    @override
    def get(self, *args, **kwargs):
        kwargs.setdefault("proxies", proxies)
        try:
            r = super().get(*args, **kwargs)
        except Exception as e:
            raise exceptions.FetchError(e)
        if self.error_handling:
            self.check_response(r)
        return r

    @override
    def post(self, *args, **kwargs):
        kwargs.setdefault("proxies", proxies)
        try:
            r = super().post(*args, **kwargs)
        except Exception as e:
            raise exceptions.FetchError(e)
        if self.error_handling:
            self.check_response(r)
        return r

    @override
    def delete(self, *args, **kwargs):
        kwargs.setdefault("proxies", proxies)
        try:
            r = super().delete(*args, **kwargs)
        except Exception as e:
            raise exceptions.FetchError(e)
        if self.error_handling:
            self.check_response(r)
        return r

    @override
    def put(self, *args, **kwargs):
        kwargs.setdefault("proxies", proxies)
        try:
            r = super().put(*args, **kwargs)
        except Exception as e:
            raise exceptions.FetchError(e)
        if self.error_handling:
            self.check_response(r)
        return r
    
    @contextmanager
    def no_error_handling(self) -> Iterator[None]:
        val_before = self.error_handling
        self.error_handling = False
        try:
            yield
        finally:
            self.error_handling = val_before
    
    @contextmanager
    def yes_error_handling(self) -> Iterator[None]:
        val_before = self.error_handling
        self.error_handling = True
        try:
            yield
        finally:
            self.error_handling = val_before

requests = Requests()
