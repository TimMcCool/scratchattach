from __future__ import annotations
import _asyncio
from collections.abc import Callable
from typing import Union, ParamSpec, TypeVar, Generic, Any, cast
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


async def join_launched_task_prim(task: LaunchedTask[P, Coroutine[Any, Any, O]]) -> O:
    return await task._task
