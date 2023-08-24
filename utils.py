import asyncio
import datetime
import logging
import logging.handlers
import os

from dotenv import find_dotenv, load_dotenv

import constants


def convert_to_second(time: str):
    dt = datetime.datetime.strptime(time, "%H:%M:%S") - datetime.datetime(1900, 1, 1)
    return dt.total_seconds()


def convert_to_time(seconds: int):
    return str(datetime.timedelta(seconds=seconds))


def get_time():
    dt = datetime.datetime.now().time()
    timestr = f"{dt.hour}:{dt.minute}:{dt.second}"
    return timestr


def get_env(key: str) -> str:
    load_dotenv(find_dotenv())
    TOKEN = os.environ.get(key)
    return TOKEN


def setup_logger(name: str, level=logging.INFO):
    logger = logging.getLogger(name)
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

    def close_remaning_tasks():
        tasks = asyncio.all_tasks()
        print(f"Closing {len(tasks)} remaining tasks...")
        for task in tasks:
            task.cancel()

    try:
        remove_dirs(curr_dir=constants.CUR_PATH)
        close_remaning_tasks()
    except RuntimeError as err:
        print("No more remaining tasks")
    except Exception as e:
        print("There are some errors when trying to delete garbages:", e)
    finally:
        print("Cleanup completed.")


class Timer:
    """Auto execute a task when the time is out.
    This designed for auto disconnect feature."""

    def __init__(self, callback) -> None:
        self.__callback = callback
        self.__task = asyncio.create_task(self.__job())

    async def __job(self):
        await asyncio.sleep(constants.VOICE_TIMEOUT)
        await self.__callback

    def cancel(self):
        self.__task.cancel()
