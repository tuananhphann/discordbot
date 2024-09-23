import asyncio
import logging
import logging.handlers
import os
import time
from datetime import datetime, timedelta
from logging import Logger
from typing import Union, Callable
import functools

import constants
from dotenv import find_dotenv, load_dotenv


def timing_sync(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:.4f} seconds.")
        return result

    return wrapper


def timing_async(func):
    """
    Decorator to measure the execution time of a function (both sync and async).
    """

    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:.4f} seconds.")
        return result

    return wrapper


def to_thread(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)

    return wrapper


def convert_to_second(time: str) -> float:
    parsed_datetime: datetime = datetime.strptime(time, "%H:%M:%S")
    dt: timedelta = parsed_datetime - datetime(1900, 1, 1)
    return dt.total_seconds()


def convert_to_time(seconds: float) -> str:
    return str(timedelta(seconds=seconds))


def get_time():
    dt = datetime.now().time()
    timestr = f"{dt.hour}:{dt.minute}:{dt.second}"
    return timestr


def get_env(key: str) -> Union[str, None]:
    load_dotenv(dotenv_path=find_dotenv())
    TOKEN: str | None = os.environ.get(key)
    return TOKEN


def setup_logger(name: str, level=logging.DEBUG) -> None:
    logger: Logger = logging.getLogger(name)
    logger.setLevel(level)
    handler = logging.handlers.RotatingFileHandler(
        filename=constants.CUR_PATH + "/discord.log",
        encoding="utf-8",
        maxBytes=32 * 1024 * 1024,  # 32 MiB
        backupCount=5,  # Rotate through 5 files
    )
    dt_fmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(
        "[{asctime}] [{levelname:<8}] {name}: {message}", dt_fmt, style="{"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def cleanup():
    """Clean garbages after bot end."""
    import shutil

    def remove_dirs(curr_dir="./", del_dirs=["temp_folder", "__pycache__"]):
        for del_dir in del_dirs:
            if del_dir in os.listdir(curr_dir):
                shutil.rmtree(os.path.join(curr_dir, del_dir))

        for dir in os.listdir(curr_dir):
            dir = os.path.join(curr_dir, dir)
            if os.path.isdir(dir):
                remove_dirs(dir, del_dirs)

    try:
        remove_dirs(curr_dir=constants.CUR_PATH)
    except Exception as e:
        print("There was some errors when trying to delete garbages:", e)
    finally:
        print("Cleanup completed.")


class Timer:
    """Auto execute a task when the time is out.
    This designed for auto disconnect feature."""

    def __init__(self, callback, ctx) -> None:
        self.__callback = callback
        self.ctx = ctx
        self.__task = asyncio.create_task(self.__job())

    async def __job(self):
        await asyncio.sleep(constants.VOICE_TIMEOUT)
        await self.__callback(self.ctx)

    def cancel(self):
        self.__task.cancel()
