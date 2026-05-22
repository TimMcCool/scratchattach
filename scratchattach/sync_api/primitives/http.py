from __future__ import annotations
from types import TracebackType
from collections.abc import Iterable, Mapping
from typing import Optional, Self, cast, Any, Sequence, SupportsInt, BinaryIO, TYPE_CHECKING

if TYPE_CHECKING:
    from _typeshed import SupportsKeysAndGetItem
from scratchattach._shared import http as shared_http
import requests
from requests import cookies as requests_cookies

HTTPOptions = shared_http.HTTPOptions


class _HTTPResponse:
    _sync_response: requests.Response

    def text(self) -> str:
        return self._sync_response.text

    def content(self) -> bytes:
        return self._sync_response.content

    def json(self) -> Any:
        return self._sync_response.json()

    @property
    def headers(self) -> Mapping[str, str]:
        """
        Headers are case-insensitive.
        """
        return self._sync_response.headers

    def get_all_headers_for_key(self, key: str) -> list[str]:
        return self._sync_response.raw.headers.getlist(key)

    @property
    def status_code(self) -> int:
        return self._sync_response.status_code


class _WrappedHTTPResponse:
    _response: requests.Response

    def __init__(self, response: requests.Response):
        self._response = response

    def __enter__(self) -> _HTTPResponse:
        response = _HTTPResponse()
        response._sync_response = self._response
        return response

    def __exit__(
        self, exc_type: Optional[type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]
    ) -> None:
        self._response.close()


class DummyCookieJar(requests_cookies.RequestsCookieJar):
    def set_cookie(self, *args, **kwargs):
        pass

    def update(self, *args, **kwargs):
        pass

    def copy(self):
        return DummyCookieJar()

    def __setitem__(self, name, value):
        pass

    def set(self, *args, **kwargs):
        pass


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
    _http_session: requests.Session

    def __init__(self):
        self._cookies = {}
        self._headers = {}
        self._http_session = requests.Session()
        self._http_session.cookies = DummyCookieJar()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self, exc_type: Optional[type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]
    ) -> None:
        pass

    @staticmethod
    def _get_params_kwarg(params: Any) -> Any:
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
    ) -> tuple[list[tuple[str, Any]] | None, list[tuple[str, BinaryIO | bytes]] | None]:
        processed_data = None
        processed_files = None
        if data is not None:
            if isinstance(data, shared_http.SupportsItems):
                data = cast(Any, data.items())
            processed_data = list(cast(Iterable[tuple[str, Any]], data))
        if files is not None:
            if isinstance(files, shared_http.SupportsItems):
                files = cast(Any, files.items())
            processed_files = list(cast(Iterable[tuple[str, BinaryIO | bytes]], files))
        return (processed_data, processed_files)

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

    def _get_kwargs(self, options: HTTPOptions) -> dict[str, Any]:  # noqa: C901
        kwargs: dict[str, Any] = {}
        if options.params is not None:
            kwargs["params"] = self._get_params_kwarg(options.params)
        if options.content is not None and options.data is not None:
            raise ValueError('Cannot specify both "content" and "data"')
        if options.content is not None and options.files is not None:
            raise ValueError('Cannot specify both "content" and "files"')
        if options.content is not None:
            kwargs["data"] = options.content
        if options.data is not None or options.files is not None:
            processed_data, processed_files = self._get_data_and_files_kwargs(options.data, options.files)
            if processed_data is not None:
                kwargs["data"] = processed_data
            if processed_files is not None:
                kwargs["files"] = processed_files
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
            kwargs["timeout"] = options.timeout
        return kwargs

    def get(self, url: str, options: HTTPOptions | None = None) -> _WrappedHTTPResponse:
        kwargs = self._get_kwargs(options if options is not None else shared_http._EMPTY_OPTIONS)
        return _WrappedHTTPResponse(self._http_session.get(url, **kwargs))

    def post(self, url: str, options: HTTPOptions | None = None) -> _WrappedHTTPResponse:
        kwargs = self._get_kwargs(options if options is not None else shared_http._EMPTY_OPTIONS)
        return _WrappedHTTPResponse(self._http_session.post(url, **kwargs))

    def put(self, url: str, options: HTTPOptions | None = None) -> _WrappedHTTPResponse:
        kwargs = self._get_kwargs(options if options is not None else shared_http._EMPTY_OPTIONS)
        return _WrappedHTTPResponse(self._http_session.put(url, **kwargs))

    def delete(self, url: str, options: HTTPOptions | None = None) -> _WrappedHTTPResponse:
        kwargs = self._get_kwargs(options if options is not None else shared_http._EMPTY_OPTIONS)
        return _WrappedHTTPResponse(self._http_session.delete(url, **kwargs))

    def request(self, method: shared_http.HTTPMethod, url: str, options: HTTPOptions | None = None) -> _WrappedHTTPResponse:
        kwargs = self._get_kwargs(options if options is not None else shared_http._EMPTY_OPTIONS)
        return _WrappedHTTPResponse(self._http_session.request(method.name, url, **kwargs))
