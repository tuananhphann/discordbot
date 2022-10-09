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
    TOKEN = os.environ.get("TOKEN")
    return TOKEN

def setup_logger(name: str, level = logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    handler = logging.handlers.RotatingFileHandler(
        filename=constants.CUR_PATH+'/discord.log',
        encoding='utf-8',
        maxBytes=32 * 1024 * 1024,  # 32 MiB
        backupCount=5,  # Rotate through 5 files
    )
    dt_fmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def cleanup():
    """Clean garbages after bot end."""
    import shutil
    try:
        shutil.rmtree(constants.TTS_PATH)
        shutil.rmtree(constants.CUR_PATH+r"/__pycache__")
        shutil.rmtree(constants.CUR_PATH+r"/cogs/__pycache__")
        shutil.rmtree(constants.CUR_PATH+r"/cogs/components/__pycache__")
        shutil.rmtree(constants.CUR_PATH+r"/cogs/music/__pycache__")
        shutil.rmtree(constants.CUR_PATH+r"/cogs/tts/__pycache__")
        print("Cleanup completed.")
    except:
        print("There are some errors when trying to delete garbages.")


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

