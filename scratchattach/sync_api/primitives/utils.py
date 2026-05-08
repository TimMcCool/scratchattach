from __future__ import annotations
import _asyncio
from collections.abc import Callable
from typing import Union, ParamSpec, TypeVar, Generic, Any, cast
import time
import threading
import concurrent.futures


def sleep_prim(delay: Union[int, float]):
    time.sleep(delay)


P = ParamSpec("P")
O = TypeVar("O", covariant=True)


class Task(Generic[P, O]):
    function: Callable[P, O]
    args: Any
    kwargs: Any
    available: bool


class LaunchedTask(Generic[P, O]):
    task: Task[P, O]
    _out: O
    _thread: threading.Thread


def create_task(function: Callable[P, O], *args: P.args, **kwargs: P.kwargs) -> Task[P, O]:
    task: Task[P, O] = Task()
    task.function = function
    task.args = args
    task.kwargs = kwargs
    task.available = True
    return task


def gather_concurrently_prim(*tasks: Task[Any, O]) -> list[O]:
    with concurrent.futures.ThreadPoolExecutor() as executor:
        return [cast(O, i) for i in executor.map(lambda x: x.function(*x.args, **x.kwargs), tasks)]


def launch_concurrently_prim(task: Task[P, O]) -> LaunchedTask[P, O]:
    launched_task: LaunchedTask[P, O] = LaunchedTask()

    def wrap_function():
        launched_task._out = task.function(*task.args, **task.kwargs)

    thread = threading.Thread(target=wrap_function)
    thread.start()
    launched_task.task = task
    launched_task._thread = thread
    return launched_task


A = TypeVar("A")
B = TypeVar("B")


def join_launched_task_prim(task: LaunchedTask[P, O]) -> O:
    task._thread.join()
    return task._out
