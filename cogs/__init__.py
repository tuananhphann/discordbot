import logging
import constants
import os

from .music.controller import *
from .music.playlist import *
from .music.search import *
from .music.music import *

try:
    os.mkdir(constants.TEMP_FOLDER)
    os.mkdir(constants.BOT_DATA_FOLDER)
except: None

logging.getLogger(__name__).addHandler(logging.NullHandler())