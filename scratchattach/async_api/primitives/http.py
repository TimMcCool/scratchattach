from __future__ import annotations
from types import TracebackType
from collections.abc import Iterable, Mapping
from typing import Optional, Self, cast, Any, Sequence, SupportsInt, BinaryIO, TYPE_CHECKING

if TYPE_CHECKING:
    from _typeshed import SupportsKeysAndGetItem
from scratchattach._shared import http as shared_http
import contextlib
import aiohttp

HTTPOptions = shared_http.HTTPOptions


class _HTTPResponse:
    _async_response: aiohttp.ClientResponse

    async def text(self) -> str:
        return await self._async_response.text()

    async def content(self) -> bytes:
        return await self._async_response.content.read()

    async def json(self) -> Any:
        return await self._async_response.json()

    @property
    def headers(self) -> Mapping[str, str]:
        """
        Headers are case-insensitive.
        """
        return self._async_response.headers

    def get_all_headers_for_key(self, key: str) -> list[str]:
        return self._async_response.headers.getall(key)

    @property
    def status_code(self) -> int:
        return self._async_response.status


class _WrappedHTTPResponse:
    _aiohttp_response_context_manager: aiohttp.client._BaseRequestContextManager[aiohttp.ClientResponse]

    def __init__(self, aiohttp_response_context_manager: aiohttp.client._BaseRequestContextManager[aiohttp.ClientResponse]):
        self._aiohttp_response_context_manager = aiohttp_response_context_manager

    def __enter__(self) -> None:
        raise TypeError("Use async with instead")

    def __exit__(
        self, exc_type: Optional[type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]
    ) -> None:
        pass

    async def __aenter__(self) -> _HTTPResponse:
        http_response = _HTTPResponse()
        http_response._async_response = await self._aiohttp_response_context_manager.__aenter__()
        return http_response

    async def __aexit__(self, exc_type: type[BaseException] | None, exc: BaseException | None, tb: TracebackType | None):
        await self._aiohttp_response_context_manager.__aexit__(exc_type, exc, tb)


class _HTTPSession:
    def add_cookie(self, key: str, value: str):
        self._cookies[key] = value

    def get_cookie(self, key: str) -> Optional[str]:
        return self._cookies.get(key)

    def remove_cookie(self, key: str):
        del self._cookies[key]

    def clear_cookies(self):
        self._cookies.clear()

    def update_cookies(self, new: "SupportsKeysAndGetItem[str, str]"):
        self._cookies.update(new)

    def list_cookies(self) -> Iterable[tuple[str, str]]:
        return self._cookies.items()

    def add_header(self, key: str, value: str):
        self._headers[key] = value

    def get_header(self, key: str) -> Optional[str]:
        return self._headers.get(key)

    def remove_header(self, key: str):
        del self._headers[key]

    def clear_headers(self):
        self._headers.clear()

    def update_headers(self, new: "SupportsKeysAndGetItem[str, str]"):
        self._headers.update(new)

    def list_headers(self) -> Iterable[tuple[str, str]]:
        return self._headers.items()

    _cookies: dict[str, str]
    _headers: dict[str, str]
    _http_session: aiohttp.ClientSession

    def __init__(self):
        self._cookies = {}

    def __enter__(self) -> None:
        raise TypeError("Use async with instead")

    def __exit__(
        self, exc_type: Optional[type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]
    ) -> None:
        pass

    async def __aenter__(self) -> Self:
        self._http_session = aiohttp.ClientSession(cookie_jar=aiohttp.DummyCookieJar())
        await self._http_session.__aenter__()
        return self

    async def __aexit__(
        self, exc_type: Optional[type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]
    ):
        await self._http_session.__aexit__(exc_type, exc_val, exc_tb)

    @staticmethod
    def _get_params_kwarg(
        params: Any,
    ) -> (
        None
        | str
        | Mapping[str, Sequence[str | SupportsInt] | SupportsInt]
        | Sequence[tuple[str, Sequence[str | SupportsInt] | SupportsInt]]
    ):
        if isinstance(params, shared_http.SupportsItems):
            params = params.items()
        if not isinstance(params, str) and isinstance(params, Iterable):
            new_params: Any = []
            for key, value in cast(Iterable[tuple[str, Iterable[str | SupportsInt] | SupportsInt | None]], params):
                if not isinstance(value, str) and isinstance(value, Iterable):
                    for item in value:
                        new_params.append((key, cast(str | SupportsInt, item)))
                elif value is None:
                    pass
                else:
                    new_params.append((key, cast(str | SupportsInt, value)))
            params = new_params
        return params

    @staticmethod
    def _get_data_and_files_kwargs(
        data: Iterable[tuple[str, Any]] | shared_http.SupportsItems[str, Any] | None,
        files: Iterable[tuple[str, BinaryIO | bytes]] | shared_http.SupportsItems[str, BinaryIO | bytes] | None,
    ) -> aiohttp.FormData:
        form_data = aiohttp.FormData()
        if data is not None:
            if isinstance(data, shared_http.SupportsItems):
                data = cast(Any, data.items())
            for key, value in cast(Iterable[tuple[str, Any]], data):
                form_data.add_field(key, str(value))
        if files is not None:
            if isinstance(files, shared_http.SupportsItems):
                files = cast(Any, files.items())
            for key, file_data in cast(Iterable[tuple[str, BinaryIO | bytes]], files):
                form_data.add_field(key, file_data, filename=key)
        return form_data

    @staticmethod
    def _get_headers_kwarg(
        default_headers: dict[str, str], headers: Iterable[tuple[str, str]] | shared_http.SupportsItems[str, str] | None
    ) -> dict[str, str]:
        if headers is None:
            return default_headers
        if isinstance(headers, shared_http.SupportsItems):
            headers = cast(Iterable[tuple[str, str]], headers.items())
        return default_headers | dict(headers)

    @staticmethod
    def _get_cookies_kwarg(
        default_cookies: dict[str, str], cookies: Iterable[tuple[str, str]] | shared_http.SupportsItems[str, str] | None
    ) -> dict[str, str]:
        if cookies is None:
            return default_cookies
        if isinstance(cookies, shared_http.SupportsItems):
            cookies = cast(Iterable[tuple[str, str]], cookies.items())
        return default_cookies | dict(cookies)

    def _get_kwargs(self, options: HTTPOptions) -> aiohttp.client._RequestOptions:  # noqa: C901
        kwargs: aiohttp.client._RequestOptions = {}
        if options.params is not None:
            kwargs["params"] = self._get_params_kwarg(options.params)
        if options.content is not None and options.data is not None:
            raise ValueError('Cannot specify both "content" and "data"')
        if options.content is not None and options.files is not None:
            raise ValueError('Cannot specify both "content" and "files"')
        if options.content is not None:
            kwargs["data"] = options.content
        if options.data is not None or options.files is not None:
            kwargs["data"] = self._get_data_and_files_kwargs(options.data, options.files)
        kwargs["cookies"] = self._get_cookies_kwarg(
            {} if options.disregard_default_cookies else self._cookies, options.cookies
        )
        kwargs["headers"] = self._get_headers_kwarg(
            {} if options.disregard_default_headers else self._headers, options.headers
        )
        if options.json is not shared_http._JsonEmptySentinel and (
            options.content is not None or options.data is not None or options.files is not None
        ):
            raise ValueError('Cannot specify "json" alongside "content", "data", or "files"')
        if options.json is not shared_http._JsonEmptySentinel:
            kwargs["json"] = options.json
        if options.timeout:
            kwargs["timeout"] = aiohttp.ClientTimeout(total=options.timeout, sock_connect=min(30, options.timeout))
        return kwargs

    def get(self, url: str, options: HTTPOptions | None = None) -> _WrappedHTTPResponse:
        kwargs = self._get_kwargs(options) if options is not None else {}
        return _WrappedHTTPResponse(self._http_session.get(url, **kwargs))

    def post(self, url: str, options: HTTPOptions | None = None) -> _WrappedHTTPResponse:
        kwargs = self._get_kwargs(options) if options is not None else {}
        return _WrappedHTTPResponse(self._http_session.post(url, **kwargs))

    def put(self, url: str, options: HTTPOptions | None = None) -> _WrappedHTTPResponse:
        kwargs = self._get_kwargs(options) if options is not None else {}
        return _WrappedHTTPResponse(self._http_session.put(url, **kwargs))

    def delete(self, url: str, options: HTTPOptions | None = None) -> _WrappedHTTPResponse:
        kwargs = self._get_kwargs(options) if options is not None else {}
        return _WrappedHTTPResponse(self._http_session.delete(url, **kwargs))

    def request(self, method: shared_http.HTTPMethod, url: str, options: HTTPOptions | None = None) -> _WrappedHTTPResponse:
        kwargs = self._get_kwargs(options) if options is not None else {}
        return _WrappedHTTPResponse(self._http_session.request(method.name, url, **kwargs))
