import os

# declare some constants
CUR_PATH = os.path.dirname(os.path.realpath(__file__))
TEMP_FOLDER = CUR_PATH + r"/temp_folder"

VOICE_TIMEOUT = 10 * 60
RENEW_TIME = 6 * 60 * 60

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}
