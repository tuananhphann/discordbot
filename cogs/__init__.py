import logging

from .music.controller import *
from .music.playlist import *
from .music.search import *
from .music.music import *

logging.getLogger(__name__).addHandler(logging.NullHandler())