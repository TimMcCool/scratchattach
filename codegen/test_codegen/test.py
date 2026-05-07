from typing import Iterable, TypeVar, ParamSpec, Generic, Any, TYPE_CHECKING, Optional, cast
from collections.abc import Callable

import time

IS_ASYNC = True
if IS_ASYNC:
    from collections.abc import Awaitable
    import asyncio
else:
    import threading
    from dataclasses import dataclass


P = ParamSpec("P")
O = TypeVar("O")

if "IS_ASYNC":
    if TYPE_CHECKING:
        import threading
        from dataclasses import dataclass

        @dataclass
        class Task(Generic[O]):
            out: Optional[threading.Thread]
            thread: Optional[threading.Thread]


if "IS_ASYNC":

    def create_task(function: Callable[P, O], *args: P.args, **kwargs: P.kwargs) -> O:
        return function(*args, **kwargs)
else:

    @dataclass
    class Task(Generic[O]):  # type: ignore[no-redef]
        out: Optional[O]
        thread: Optional[threading.Thread]

    def create_task(function: Callable[P, O], *args: P.args, **kwargs: P.kwargs) -> Task[O]:  # type: ignore[misc]
        task: Task[O] = Task(None, None)  # type: ignore[arg-type]

        def wrapper(*args, **kwargs):
            task.out = function(*args, **kwargs)

        task.thread = threading.Thread(target=wrapper, args=args, kwargs=kwargs)
        return task


def sleep_prim_sync(delay: int | float):
    time.sleep(delay)


async def sleep_prim(delay: int | float):
    await asyncio.sleep(delay)


T = TypeVar("T")


def gather_prim_sync(*tasks: Task[T]) -> list[T]:
    values: list[T] = []
    threads: list[threading.Thread] = []
    for task in tasks:
        if task.thread:
            task.thread.start()

    for task in tasks:
        if task.thread:
            task.thread.join()
        values.append(cast(T, task.out))

    return values


async def gather_prim(*tasks: Awaitable[T]) -> list[T]:
    return await asyncio.gather(*tasks)


async def fetch_user_data(user_id: int, delay: int) -> dict:
    print(f"[{time.strftime('%X')}] Task {user_id}: Starting request (takes {delay}s)...")

    await sleep_prim(delay)

    print(f"[{time.strftime('%X')}] Task {user_id}: Finished request!")
    return {"user_id": user_id, "status": "success"}


async def main():
    start_time = time.perf_counter()
    print("--- Fetching data concurrently ---")

    coroutines = [
        create_task(fetch_user_data, user_id=1, delay=2),
        create_task(fetch_user_data, user_id=2, delay=3),
        create_task(fetch_user_data, user_id=3, delay=1),
    ]

    results = await gather_prim(*coroutines)

    end_time = time.perf_counter()
    total_time = end_time - start_time

    print("\n--- All tasks complete ---")
    print(f"Total time taken: {total_time:.2f} seconds")
    print("Results:", results)


if __name__ == "__main__":
    if IS_ASYNC:
        asyncio.run(main())
    else:
        main()
