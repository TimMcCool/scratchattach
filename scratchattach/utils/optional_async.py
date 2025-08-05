from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Generator, Callable
from typing import Generic, TypeVar, ParamSpec, Optional, Union, Any
from functools import wraps
import asyncio
import time

from . import requests

P = ParamSpec("P")
R = TypeVar("R")

class CallableAwaitable(Generic[R], ABC, Awaitable[R]):
    result: R
    
    @abstractmethod
    def sync_impl(self) -> R:
        pass
    
    def __pos__(self) -> R:
        return self.sync_impl()
    
    @abstractmethod
    async def async_impl(self) -> R:
        pass
    
    def __await__(self) -> Generator[None, None, R]:
        return self.async_impl().__await__()

class OptionallyAsync(Generic[P, R], ABC):
    @abstractmethod
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> CallableAwaitable[R]:
        pass

def optionally_async(func: Callable[P, Generator[CallableAwaitable, None, R]]) -> OptionallyAsync[P, R]:
    class Wrapped(OptionallyAsync[P, R]):
        def __call__(self, *args: P.args, **kwargs: P.kwargs) -> CallableAwaitable[R]:
            class Implementation(CallableAwaitable[R]):
                def sync_impl(self) -> R:
                    i = func(*args, **kwargs)
                    try:
                        while True:
                            c = next(i)
                            c.result = +c
                    except StopIteration as excp:
                        return excp.value
                
                async def async_impl(self) -> R:
                    i = func(*args, **kwargs)
                    try:
                        while True:
                            c = next(i)
                            c.result = await c
                    except StopIteration as excp:
                        return excp.value
            
            return Implementation()
    return Wrapped()

def make_async(func: Callable[P, Generator[CallableAwaitable, None, R]]) -> Callable[P, Awaitable[R]]:
    @wraps(func)
    async def async_impl(*args: P.args, **kwargs: P.kwargs) -> R:
        i = func(*args, **kwargs)
        try:
            while True:
                c = next(i)
                c.result = await c
        except StopIteration as excp:
            return excp.value
    return async_impl

def make_sync(func: Callable[P, Generator[CallableAwaitable, None, R]]) -> Callable[P, R]:
    @wraps(func)
    def sync_impl(*args: P.args, **kwargs: P.kwargs) -> R:
        i = func(*args, **kwargs)
        try:
            while True:
                c = next(i)
                c.result = +c
        except StopIteration as excp:
            return excp.value
    return sync_impl

class CASleep(CallableAwaitable[bool]):
    amount: float
    
    def __init__(self, amount: float) -> None:
        self.amount = amount
    
    def sync_impl(self):
        time.sleep(self.amount)
        return True
    
    async def async_impl(self):
        await asyncio.sleep(self.amount)
        return True

def oa_sleep(amount: float):
    return CASleep(amount)

class CARequest(CallableAwaitable["requests.AnyHTTPResponse"]):
    requests_session: requests.OAHTTPSession
    method: requests.HTTPMethod
    url: str
    cookies: Optional[dict[str, str]]
    headers: Optional[dict[str, str]]
    params: Optional[dict[str, str]]
    data: Optional[Union[dict[str, str], str]]
    json: Optional[dict[str, str]]
    
    def __init__(
        self,
        requests_session: requests.OAHTTPSession,
        method: requests.HTTPMethod,
        url: str,
        *,
        cookies: Optional[dict[str, str]] = None,
        headers: Optional[dict[str, str]] = None,
        params: Optional[dict[str, str]] = None,
        data: Optional[Union[dict[str, str], str]] = None,
        json: Optional[Any] = None
    ) -> None:
        self.requests_session = requests_session
        self.method = method
        self.url = url
        self.cookies = cookies
        self.headers = headers
        self.params = params
        self.data = data
        self.json = json
    
    def sync_impl(self):
        return self.requests_session.sync_request(
            method = self.method,
            url = self.url,
            cookies = self.cookies,
            headers = self.headers,
            params = self.params,
            data = self.data,
            json = self.json
        )
    
    async def async_impl(self):
        return await self.requests_session.async_request(
            method = self.method,
            url = self.url,
            cookies = self.cookies,
            headers = self.headers,
            params = self.params,
            data = self.data,
            json = self.json
        )
