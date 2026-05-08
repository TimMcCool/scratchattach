from __future__ import annotations
import _asyncio
from collections.abc import Callable
from typing import Union, ParamSpec, TypeVar, Generic, Any, cast, Optional, overload, Literal
import time

if "IS_PRE_CODEGEN":
    CTYPES_PRESENT = True
    import ctypes
    import threading
    import concurrent.futures
    import asyncio
    from collections.abc import Awaitable, Coroutine
else:
    if "IS_ASYNC":
        CTYPES_PRESENT = False
        import asyncio
        from collections.abc import Awaitable, Coroutine
    else:
        try:
            import ctypes

            CTYPES_PRESENT = True
        except Exception:
            CTYPES_PRESENT = False
        import threading
        import concurrent.futures


def sleep_prim_sync(delay: Union[int, float]):
    time.sleep(delay)


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
    if "IS_PRE_CODEGEN":
        _out: O
        _task: asyncio.Task[Any]
        _thread: threading.Thread
    else:
        if "IS_ASYNC":
            _task: asyncio.Task[Any]  # type: ignore[no-redef]
        else:
            _out: O  # type: ignore[no-redef]
            _thread: threading.Thread  # type: ignore[no-redef]


def create_task(function: Callable[P, O], *args: P.args, **kwargs: P.kwargs) -> Task[P, O]:
    task: Task[P, O] = Task()
    task.function = function
    task.args = args
    task.kwargs = kwargs
    task.available = True
    return task


def gather_concurrently_prim_sync(*tasks: Task[Any, O]) -> list[O]:
    with concurrent.futures.ThreadPoolExecutor() as executor:
        return [cast(O, i) for i in executor.map(lambda x: x.function(*x.args, **x.kwargs), tasks)]


async def gather_concurrently_prim(*tasks: Task[Any, Awaitable[O]]) -> list[O]:
    for task in tasks:
        if not task.available:
            raise ValueError("Task is already used.")
        task.available = False
    return await asyncio.gather(*(task.function(*task.args, **task.kwargs) for task in tasks))


def launch_concurrently_prim_sync(task: Task[P, O]) -> LaunchedTask[P, O]:
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


async def launch_concurrently_prim(
    task: Task[P, Coroutine[A, B, O]],
) -> LaunchedTask[P, Coroutine[A, B, O]]:
    _task = asyncio.create_task(task.function(*task.args, **task.kwargs))
    launched_task: LaunchedTask[P, Coroutine[A, B, O]] = LaunchedTask()
    launched_task.task = task
    launched_task._task = _task
    return launched_task


@overload
def join_launched_task_prim_sync(task: LaunchedTask[P, O]) -> O:
    pass


@overload
def join_launched_task_prim_sync(
    task: LaunchedTask[P, O], timeout: Union[float, int]
) -> Optional[O]:
    pass


def join_launched_task_prim_sync(
    task: LaunchedTask[P, O], timeout: Optional[Union[float, int]] = None
) -> Optional[O]:
    task._thread.join(timeout)
    if task._thread.is_alive():
        return None
    return task._out


@overload
async def join_launched_task_prim(task: LaunchedTask[P, Coroutine[Any, Any, O]]) -> O:
    pass


@overload
async def join_launched_task_prim(
    task: LaunchedTask[P, Coroutine[Any, Any, O]], timeout: Union[float, int]
) -> Optional[O]:
    pass


async def join_launched_task_prim(
    task: LaunchedTask[P, Coroutine[Any, Any, O]], timeout: Optional[Union[float, int]] = None
) -> Optional[O]:
    try:
        return await asyncio.wait_for(asyncio.shield(task._task), timeout)
    except TimeoutError:
        return None


if "IS_PRE_CODEGEN":

    def _raise_in_thread(thread: threading.Thread, exc_type: type[BaseException]) -> None: ...


if not "IS_ASYNC":

    def _raise_in_thread(thread: threading.Thread, exc_type: type[BaseException]) -> None:
        if not CTYPES_PRESENT:
            raise NotImplementedError(
                "Sending exceptions to threads is not supported in this Python version."
            )

        if not thread.is_alive():
            raise ValueError("Thread is not alive.")

        thread_id = thread.ident
        if thread_id is None:
            raise ValueError("Thread has no ident.")

        result = ctypes.pythonapi.PyThreadState_SetAsyncExc(
            ctypes.c_ulong(thread_id),
            ctypes.py_object(exc_type),
        )

        if result == 0:
            raise ValueError("Thread ident is invalid.")

        if result > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(
                ctypes.c_ulong(thread_id),
                None,
            )
            raise SystemError("PyThreadState_SetAsyncExc failed.")


@overload
def kill_launched_task_prim_sync(
    task: LaunchedTask[P, O], *, exception_interval: Union[float, int] = 0.1
) -> Literal[True]:
    """
    Sends exceptions to the underlying concurrency primitive.
    May also try to use the recommended way of cancelling the primitive if there is one.
    Returns whether the task was actually killed.
    """


@overload
def kill_launched_task_prim_sync(
    task: LaunchedTask[P, O],
    timeout: Union[float, int],
    *,
    exception_interval: Union[float, int] = 0.1,
) -> bool:
    """
    Sends exceptions to the underlying concurrency primitive.
    May also try to use the recommended way of cancelling the primitive if there is one.
    Returns whether the task was actually killed.
    """


def kill_launched_task_prim_sync(
    task: LaunchedTask[P, O],
    timeout: Optional[Union[float, int]] = None,
    *,
    exception_interval: Union[float, int] = 0.1,
) -> bool:
    has_timeout, timeout_end = (
        (True, time.time() + timeout) if timeout is not None else (False, None)
    )
    while (not has_timeout) or (timeout_end is not None and time.time() <= timeout_end):
        if not task._thread.is_alive():
            break
        _raise_in_thread(task._thread, SystemExit)
        time.sleep(exception_interval)
    if has_timeout and timeout_end is not None and time.time() > timeout_end:
        return False
    return True


@overload
async def kill_launched_task_prim(
    task: LaunchedTask[P, O], *, exception_interval: Union[float, int] = 0.1
) -> Literal[True]:
    """
    Sends exceptions to the underlying concurrency primitive.
    May also try to use the recommended way of cancelling the primitive if there is one.
    Returns whether the task was actually killed.
    """


@overload
async def kill_launched_task_prim(
    task: LaunchedTask[P, O],
    timeout: Union[float, int],
    *,
    exception_interval: Union[float, int] = 0.1,
) -> bool:
    """
    Sends exceptions to the underlying concurrency primitive.
    May also try to use the recommended way of cancelling the primitive if there is one.
    Returns whether the task was actually killed.
    """


async def kill_launched_task_prim(
    task: LaunchedTask[P, O],
    timeout: Optional[Union[float, int]] = None,
    *,
    exception_interval: Union[float, int] = 0.1,
) -> bool:
    has_timeout, timeout_end = (
        (True, time.time() + timeout) if timeout is not None else (False, None)
    )
    if task._task.cancel():
        return True
    while (not has_timeout) or (timeout_end is not None and time.time() <= timeout_end):
        if not task._task.done():
            break
        task._task.set_exception(SystemExit)
        await asyncio.sleep(exception_interval)
    if has_timeout and timeout_end is not None and time.time() > timeout_end:
        return False
    return True


# async def task_1():
#     print("Starting task 1...")
#     await sleep_prim(2)
#     print("Task 1 done.")


# async def task_2(msg: Any):
#     print("Starting task 2...")
#     await sleep_prim(1)
#     print("Task 2 says:", msg)
#     print("Task 2 done.")


# async def task_3(delay: Union[float, int]):
#     print("Starting task 3...")
#     await sleep_prim(delay)
#     print("Task 3 done.")


# async def main():
#     await gather_concurrently_prim(
#         create_task(task_1), create_task(task_2, msg="Hello there!"), create_task(task_3, 3)
#     )
#     print("Launching task...")
#     task = await launch_concurrently_prim(create_task(task_3, 5))
#     print("Launched task.")
#     await sleep_prim(4)
#     print("Joining task...")
#     await join_launched_task_prim(task)
#     print("Task done.")


# if __name__ == "__main__":
#     if "IS_ASYNC":
#         asyncio.run(main())
#     else:
#         main()
