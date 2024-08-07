import argparse
import asyncio
import threading
import time
from concurrent.futures import ThreadPoolExecutor


async def do_press(start):
    await asyncio.sleep(0.2)
    print(f"{start} -- {time.monotonic() - start}")
    return 0


def do_press_sync(start):
    time.sleep(0.2)
    print(f"{start} -- {time.monotonic() - start}")


async def asyncio_worker(qpm: int, duration: int):
    interval: float = 60.0 / qpm
    end_time = time.monotonic() + duration
    tasks = []

    while time.monotonic() < end_time:
        start = time.monotonic()
        task = asyncio.create_task(do_press(start))
        tasks.append(task)
        elapsed = time.monotonic() - start
        await asyncio.sleep(max(0.0, interval - elapsed))
    await asyncio.gather(*tasks)


async def asyncio_worker_with_timesleep(qpm: int, duration: int):
    interval: float = 60.0 / qpm
    end_time = time.monotonic() + duration
    tasks = []
    while time.monotonic() < end_time:
        start = time.monotonic()
        task = asyncio.create_task(do_press(start))
        tasks.append(task)
        elapsed = time.monotonic() - start
        time.sleep(max(0.0, interval - elapsed))
    await asyncio.gather(*tasks)


def thread_worker(qpm: int, duration: int):
    interval: float = 60.0 / qpm
    end_time = time.monotonic() + duration
    while time.monotonic() < end_time:
        start = time.monotonic()
        do_press_sync(start)
        elapsed = time.monotonic() - start
        time.sleep(max(0.0, interval - elapsed))


def main(qpm: int, duration: int, case: str = "async", thread_nums: int = None):
    handler = asyncio_worker
    if case == "thread":
        handler = thread_worker
        with ThreadPoolExecutor(max_workers=thread_nums) as executor:
            interval = 60.0 / qpm
            end_time = time.monotonic() + duration
            while time.monotonic() < end_time:
                start = time.monotonic()
                executor.submit(do_press_sync, start)
                elapsed = time.monotonic() - start
                time.sleep(max(0.0, interval - elapsed))
        return
    elif case == "async_timesleep":
        handler = asyncio_worker_with_timesleep
    elif case == "async":
        handler = asyncio_worker
    asyncio.run(handler(qpm, duration))
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--qpm", type=int, help="QPM level")
    parser.add_argument("--duration", type=int, help="Duration in seconds")
    parser.add_argument("--case", choices=["async", "async_timesleep", "thread"], help="Case")
    parser.add_argument("--thread_nums", type=int, help="Number of threads")
    args = parser.parse_args()
    main(**vars(args))

