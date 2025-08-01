from __future__ import annotations
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Generator, Callable
from typing import Generic, TypeVar, ParamSpec
import asyncio
import time

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

class CASleep(CallableAwaitable[None]):
    amount: float
    
    def __init__(self, amount: float) -> None:
        self.amount = amount
    
    def sync_impl(self):
        return time.sleep(self.amount)
    
    async def async_impl(self):
        return await asyncio.sleep(self.amount)
    
def oa_sleep(amount: float):
    return CASleep(amount)
