from __future__ import annotations

from collections.abc import MutableMapping, Iterator
from typing import Optional
from contextlib import contextmanager

from typing_extensions import override
from requests import Session as HTTPSession
from requests import Response

from . import exceptions

proxies: Optional[MutableMapping[str, str]] = None

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
