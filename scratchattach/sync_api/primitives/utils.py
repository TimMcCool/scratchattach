from __future__ import annotations
from collections.abc import Callable
from typing import Union, ParamSpec, TypeVar, Generic, Any, cast, Optional, overload, Literal
import time

try:
    import ctypes

    CTYPES_PRESENT = True
except Exception:
    CTYPES_PRESENT = False
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


@overload
def join_launched_task_prim(task: LaunchedTask[P, O]) -> O:
    pass


@overload
def join_launched_task_prim(task: LaunchedTask[P, O], timeout: Union[float, int]) -> Optional[O]:
    pass


def join_launched_task_prim(task: LaunchedTask[P, O], timeout: Optional[Union[float, int]] = None) -> Optional[O]:
    task._thread.join(timeout)
    if task._thread.is_alive():
        return None
    return task._out


def _raise_in_thread(thread: threading.Thread, exc_type: type[BaseException]) -> None:
    if not CTYPES_PRESENT:
        raise NotImplementedError("Sending exceptions to threads is not supported in this Python version.")
    if not thread.is_alive():
        raise ValueError("Thread is not alive.")
    thread_id = thread.ident
    if thread_id is None:
        raise ValueError("Thread has no ident.")
    result = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_ulong(thread_id), ctypes.py_object(exc_type))
    if result == 0:
        raise ValueError("Thread ident is invalid.")
    if result > 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_ulong(thread_id), None)
        raise SystemError("PyThreadState_SetAsyncExc failed.")


@overload
def kill_launched_task_prim(task: LaunchedTask[P, O], *, exception_interval: Union[float, int] = 0.1) -> Literal[True]:
    """
    Sends exceptions to the underlying concurrency primitive.
    May also try to use the recommended way of cancelling the primitive if there is one.
    Returns whether the task was actually killed.
    """


@overload
def kill_launched_task_prim(
    task: LaunchedTask[P, O], timeout: Union[float, int], *, exception_interval: Union[float, int] = 0.1
) -> bool:
    """
    Sends exceptions to the underlying concurrency primitive.
    May also try to use the recommended way of cancelling the primitive if there is one.
    Returns whether the task was actually killed.
    """


def kill_launched_task_prim(
    task: LaunchedTask[P, O], timeout: Optional[Union[float, int]] = None, *, exception_interval: Union[float, int] = 0.1
) -> bool:
    has_timeout, timeout_end = (True, time.time() + timeout) if timeout is not None else (False, None)
    while not has_timeout or (timeout_end is not None and time.time() <= timeout_end):
        if not task._thread.is_alive():
            break
        _raise_in_thread(task._thread, SystemExit)
        time.sleep(exception_interval)
    if has_timeout and timeout_end is not None and (time.time() > timeout_end):
        return False
    return True
