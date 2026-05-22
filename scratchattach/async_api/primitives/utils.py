from __future__ import annotations
from collections.abc import Callable
from typing import Union, ParamSpec, TypeVar, Generic, Any, cast, Optional, overload, Literal
import time

CTYPES_PRESENT = False
import asyncio
from collections.abc import Awaitable, Coroutine


async def sleep_prim(delay: Union[int, float]):
    await asyncio.sleep(delay)


P = ParamSpec("P")
O = TypeVar("O", covariant=True)


class Task(Generic[P, O]):
    function: Callable[P, O]
    args: Any
    kwargs: Any
    available: bool


class LaunchedTask(Generic[P, O]):
    task: Task[P, O]
    _task: asyncio.Task[Any]


def create_task(function: Callable[P, O], *args: P.args, **kwargs: P.kwargs) -> Task[P, O]:
    task: Task[P, O] = Task()
    task.function = function
    task.args = args
    task.kwargs = kwargs
    task.available = True
    return task


async def gather_concurrently_prim(*tasks: Task[Any, Awaitable[O]]) -> list[O]:
    for task in tasks:
        if not task.available:
            raise ValueError("Task is already used.")
        task.available = False
    return await asyncio.gather(*(task.function(*task.args, **task.kwargs) for task in tasks))


A = TypeVar("A")
B = TypeVar("B")


async def launch_concurrently_prim(task: Task[P, Coroutine[A, B, O]]) -> LaunchedTask[P, Coroutine[A, B, O]]:
    _task = asyncio.create_task(task.function(*task.args, **task.kwargs))
    launched_task: LaunchedTask[P, Coroutine[A, B, O]] = LaunchedTask()
    launched_task.task = task
    launched_task._task = _task
    return launched_task


@overload
async def join_launched_task_prim(task: LaunchedTask[P, Coroutine[Any, Any, O]]) -> O:
    pass


@overload
async def join_launched_task_prim(task: LaunchedTask[P, Coroutine[Any, Any, O]], timeout: Union[float, int]) -> Optional[O]:
    pass


async def join_launched_task_prim(
    task: LaunchedTask[P, Coroutine[Any, Any, O]], timeout: Optional[Union[float, int]] = None
) -> Optional[O]:
    try:
        return await asyncio.wait_for(asyncio.shield(task._task), timeout)
    except TimeoutError:
        return None


@overload
async def kill_launched_task_prim(task: LaunchedTask[P, O], *, exception_interval: Union[float, int] = 0.1) -> Literal[True]:
    """
    Sends exceptions to the underlying concurrency primitive.
    May also try to use the recommended way of cancelling the primitive if there is one.
    Returns whether the task was actually killed.
    """


@overload
async def kill_launched_task_prim(
    task: LaunchedTask[P, O], timeout: Union[float, int], *, exception_interval: Union[float, int] = 0.1
) -> bool:
    """
    Sends exceptions to the underlying concurrency primitive.
    May also try to use the recommended way of cancelling the primitive if there is one.
    Returns whether the task was actually killed.
    """


async def kill_launched_task_prim(
    task: LaunchedTask[P, O], timeout: Optional[Union[float, int]] = None, *, exception_interval: Union[float, int] = 0.1
) -> bool:
    has_timeout, timeout_end = (True, time.time() + timeout) if timeout is not None else (False, None)
    if task._task.cancel():
        return True
    while not has_timeout or (timeout_end is not None and time.time() <= timeout_end):
        if not task._task.done():
            break
        task._task.set_exception(SystemExit)
        await asyncio.sleep(exception_interval)
    if has_timeout and timeout_end is not None and (time.time() > timeout_end):
        return False
    return True
