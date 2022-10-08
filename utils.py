import datetime
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
