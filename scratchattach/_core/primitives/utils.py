from __future__ import annotations
import _asyncio
from collections.abc import Callable
from typing import Union, ParamSpec, TypeVar, Generic, Any, cast

if "IS_PRE_CODEGEN":
    import time
    import threading
    import concurrent.futures
    import asyncio
    from collections.abc import Awaitable, Coroutine
else:
    if "IS_ASYNC":
        import asyncio
        from collections.abc import Awaitable, Coroutine
    else:
        import time
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


def join_launched_task_prim_sync(task: LaunchedTask[P, O]) -> O:
    task._thread.join()
    return task._out

async def join_launched_task_prim(task: LaunchedTask[P, Coroutine[Any, Any, O]]) -> O:
    return await task._task


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
