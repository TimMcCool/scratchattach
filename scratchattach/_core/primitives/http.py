from __future__ import annotations
from types import TracebackType
from collections.abc import Iterable
from typing import Optional, Self, cast, Any, Sequence, SupportsInt, BinaryIO

from scratchattach._shared import http as shared_http

if "IS_PRE_CODEGEN":
    import contextlib
    import aiohttp
    import requests
    from requests import cookies as requests_cookies
else:
    if "IS_ASYNC":
        import contextlib
        import aiohttp
    else:
        import requests
        from requests import cookies as requests_cookies


HTTPOptions = shared_http.HTTPOptions


if "IS_ASYNC":

    class _HTTPResponse:
        _async_response: aiohttp.ClientResponse
        if "IS_PRE_CODEGEN":
            _sync_response: requests.Response

    class _WrappedHTTPResponse:
        _aiohttp_response_context_manager: aiohttp.client._BaseRequestContextManager[
            aiohttp.ClientResponse
        ]

        def __init__(
            self,
            aiohttp_response_context_manager: aiohttp.client._BaseRequestContextManager[
                aiohttp.ClientResponse
            ],
        ):
            self._aiohttp_response_context_manager = aiohttp_response_context_manager

        def __enter__(self) -> None:
            raise TypeError("Use async with instead")

        def __exit__(
            self,
            exc_type: Optional[type[BaseException]],
            exc_val: Optional[BaseException],
            exc_tb: Optional[TracebackType],
        ) -> None:
            # __exit__ should exist in pair with __enter__ but never executed
            pass  # pragma: no cover

        async def __aenter__(self) -> _HTTPResponse:
            http_response = _HTTPResponse()
            http_response._async_response = (
                await self._aiohttp_response_context_manager.__aenter__()
            )
            return http_response

        async def __aexit__(
            self,
            exc_type: type[BaseException] | None,
            exc: BaseException | None,
            tb: TracebackType | None,
        ):
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
            self,
            exc_type: Optional[type[BaseException]],
            exc_val: Optional[BaseException],
            exc_tb: Optional[TracebackType],
        ) -> None:
            # __exit__ should exist in pair with __enter__ but never executed
            pass  # pragma: no cover

        async def __aenter__(self) -> Self:
            self._http_session = aiohttp.ClientSession(cookie_jar=aiohttp.DummyCookieJar())
            await self._http_session.__aenter__()
            return self

        async def __aexit__(
            self,
            exc_type: Optional[type[BaseException]],
            exc_val: Optional[BaseException],
            exc_tb: Optional[TracebackType],
        ):
            await self._http_session.__aexit__(exc_type, exc_val, exc_tb)

        def _get_kwargs(self, options: HTTPOptions) -> aiohttp.client._RequestOptions:
            kwargs: aiohttp.client._RequestOptions = {}
            if options.params is not None:
                params: Any = options.params
                if isinstance(params, shared_http.SupportsItems):
                    params = params.items()
                if not isinstance(params, str) and isinstance(params, Iterable):
                    new_params: Any = []
                    for key, value in cast(
                        Iterable[tuple[str, Iterable[str | SupportsInt] | SupportsInt]], params
                    ):
                        if not isinstance(value, str) and isinstance(value, Iterable):
                            for item in value:
                                new_params.append((key, cast(str | SupportsInt, item)))
                        else:
                            new_params.append((key, cast(str | SupportsInt, value)))
                    params = new_params
                kwargs["params"] = params  # type: ignore[typeddict-item]
            if options.content is not None and options.data is not None:
                raise ValueError("Cannot specify both \"content\" and \"data\"")
            if options.content is not None and options.files is not None:
                raise ValueError("Cannot specify both \"content\" and \"files\"")
            if options.content is not None:
                kwargs["data"] = options.content
            if options.data is not None or options.files is not None:
                form_data = aiohttp.FormData()
                if options.data is not None:
                    data = options.data
                    if isinstance(data, shared_http.SupportsItems):
                        data = data.items()
                    for key, value in cast(Iterable[tuple[str, Any]], data):
                        form_data.add_field(key, str(value))
                if options.files is not None:
                    files = options.files
                    if isinstance(files, shared_http.SupportsItems):
                        files = files.items()
                    for key, file_data in cast(Iterable[tuple[str, BinaryIO | bytes]], files):
                        form_data.add_field(key, file_data, filename=key)
                kwargs["data"] = form_data
            merged_cookies = self._cookies.copy()
            if options.cookies is not None:
                cookies = options.cookies
                if isinstance(cookies, shared_http.SupportsItems):
                    cookies = cookies.items()
                merged_cookies.update(dict(cast(Iterable[tuple[str, str]], cookies)))
            kwargs["cookies"] = merged_cookies
            if options.headers is not None:
                headers = options.headers
                if isinstance(headers, shared_http.SupportsItems):
                    headers = headers.items()
                kwargs["headers"] = dict(cast(Iterable[tuple[str, str]], headers))
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
else:

    class _HTTPResponse:  # type: ignore[no-redef]
        _sync_response: requests.Response

    class _WrappedHTTPResponse:  # type: ignore[no-redef]
        _response: requests.Response

        def __init__(self, response: requests.Response):
            self._response = response

        def __enter__(self) -> _HTTPResponse:
            response = _HTTPResponse()
            response._sync_response = self._response
            return response

        def __exit__(
            self,
            exc_type: Optional[type[BaseException]],
            exc_val: Optional[BaseException],
            exc_tb: Optional[TracebackType],
        ) -> None:
            pass

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

    class _HTTPSession:  # type: ignore[no-redef]
        def add_cookie(self, key: str, value: str):
            self._cookies[key] = value

        def get_cookie(self, key: str) -> Optional[str]:
            return self._cookies.get(key)

        def remove_cookie(self, key: str):
            del self._cookies[key]

        def list_cookies(self) -> Iterable[tuple[str, str]]:
            return self._cookies.items()

        _cookies: dict[str, str]

        _http_session: requests.Session

        def __init__(self):
            self._cookies = {}
            self._http_session = requests.Session()
            self._http_session.cookies = DummyCookieJar()

        def _get_kwargs(self, options: HTTPOptions) -> dict[str, Any]:
            kwargs: dict[str, Any] = {}

            if options.params is not None:
                params: Any = options.params
                if isinstance(params, shared_http.SupportsItems):
                    params = params.items()
                if not isinstance(params, str) and isinstance(params, Iterable):
                    new_params: Any = []
                    for key, value in cast(
                        Iterable[tuple[str, Iterable[str | SupportsInt] | SupportsInt]], params
                    ):
                        if not isinstance(value, str) and isinstance(value, Iterable):
                            for item in value:
                                new_params.append((key, cast(str | SupportsInt, item)))
                        else:
                            new_params.append((key, cast(str | SupportsInt, value)))
                    params =  new_params
                kwargs["params"] = params
            if options.content is not None and options.data is not None:
                raise ValueError("Cannot specify both \"content\" and \"data\"")
            if options.content is not None and options.files is not None:
                raise ValueError("Cannot specify both \"content\" and \"files\"")
            if options.content is not None:
                kwargs["data"] = options.content
            if options.data is not None:
                data = options.data
                if isinstance(data, shared_http.SupportsItems):
                    data = data.items()
                kwargs["data"] = list(cast(Iterable[tuple[str, Any]], data))
            if options.files is not None:
                files = options.files
                if isinstance(files, shared_http.SupportsItems):
                    files = files.items()
                kwargs["files"] = list(cast(Iterable[tuple[str, BinaryIO | bytes]], files))
            merged_cookies = self._cookies.copy()
            if options.cookies is not None:
                cookies = options.cookies
                if isinstance(cookies, shared_http.SupportsItems):
                    cookies = cookies.items()
                merged_cookies.update(dict(cast(Iterable[tuple[str, str]], cookies)))
            kwargs["cookies"] = merged_cookies
            if options.headers is not None:
                headers = options.headers
                if isinstance(headers, shared_http.SupportsItems):
                    headers = headers.items()
                kwargs["headers"] = dict(cast(Iterable[tuple[str, str]], headers))
            if options.json is not shared_http._JsonEmptySentinel:
                kwargs["json"] = options.json
            return kwargs

        def get(self, url: str, options: HTTPOptions) -> _WrappedHTTPResponse:
            kwargs = self._get_kwargs(options)
            return _WrappedHTTPResponse(self._http_session.get(url, **kwargs))  # type: ignore[arg-type]

        def post(self, url: str, options: HTTPOptions) -> _WrappedHTTPResponse:
            kwargs = self._get_kwargs(options)
            return _WrappedHTTPResponse(self._http_session.post(url, **kwargs))  # type: ignore[arg-type]

        def put(self, url: str, options: HTTPOptions) -> _WrappedHTTPResponse:
            kwargs = self._get_kwargs(options)
            return _WrappedHTTPResponse(self._http_session.put(url, **kwargs))  # type: ignore[arg-type]

        def delete(self, url: str, options: HTTPOptions) -> _WrappedHTTPResponse:
            kwargs = self._get_kwargs(options)
            return _WrappedHTTPResponse(self._http_session.delete(url, **kwargs))  # type: ignore[arg-type]
