import logging
import os

import constants

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())

try:
    os.mkdir(constants.TEMP_FOLDER)
except FileExistsError:
    pass
