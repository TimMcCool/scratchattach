from __future__ import annotations
from types import TracebackType
from collections.abc import Iterable, Mapping
from typing import Optional, Self, cast, Any, Sequence, SupportsInt, BinaryIO
from scratchattach._shared import http as shared_http
import contextlib
import aiohttp

HTTPOptions = shared_http.HTTPOptions


class _HTTPResponse:
    _async_response: aiohttp.ClientResponse


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

    def list_cookies(self) -> Iterable[tuple[str, str]]:
        return self._cookies.items()

    _cookies: dict[str, str]
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
            for key, value in cast(Iterable[tuple[str, Iterable[str | SupportsInt] | SupportsInt]], params):
                if not isinstance(value, str) and isinstance(value, Iterable):
                    for item in value:
                        new_params.append((key, cast(str | SupportsInt, item)))
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
    def _get_headers_kwarg(headers: Iterable[tuple[str, str]] | shared_http.SupportsItems[str, str]) -> dict[str, str]:
        if isinstance(headers, shared_http.SupportsItems):
            headers = cast(Any, headers.items())
        return dict(cast(Iterable[tuple[str, str]], headers))

    def _get_kwargs(self, options: HTTPOptions) -> aiohttp.client._RequestOptions:
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
        merged_cookies = self._cookies.copy()
        if options.cookies is not None:
            cookies = options.cookies
            if isinstance(cookies, shared_http.SupportsItems):
                cookies = cookies.items()
            merged_cookies.update(dict(cast(Iterable[tuple[str, str]], cookies)))
        kwargs["cookies"] = merged_cookies
        if options.headers is not None:
            kwargs["headers"] = self._get_headers_kwarg(options.headers)
        if options.json is not shared_http._JsonEmptySentinel and (
            options.content is not None or options.data is not None or options.files is not None
        ):
            raise ValueError('Cannot specify "json" alongside "content", "data", or "files"')
        if options.json is not shared_http._JsonEmptySentinel:
            kwargs["json"] = options.json
        return kwargs

    def get(self, url: str, options: HTTPOptions) -> _WrappedHTTPResponse:
        kwargs = self._get_kwargs(options)
        return _WrappedHTTPResponse(self._http_session.get(url, **kwargs))

    def post(self, url: str, options: HTTPOptions) -> _WrappedHTTPResponse:
        kwargs = self._get_kwargs(options)
        return _WrappedHTTPResponse(self._http_session.post(url, **kwargs))

    def put(self, url: str, options: HTTPOptions) -> _WrappedHTTPResponse:
        kwargs = self._get_kwargs(options)
        return _WrappedHTTPResponse(self._http_session.put(url, **kwargs))

    def delete(self, url: str, options: HTTPOptions) -> _WrappedHTTPResponse:
        kwargs = self._get_kwargs(options)
        return _WrappedHTTPResponse(self._http_session.delete(url, **kwargs))
