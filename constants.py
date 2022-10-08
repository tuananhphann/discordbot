import os
# declare some constants 
TTS_PATH = os.path.dirname(os.path.realpath(__file__))+r"\tts_tempfolder"
CUR_PATH = os.path.dirname(os.path.realpath(__file__))
YOUTUBE_PREFIX = "https://youtube.com"
YDL_PREFIX = "https://youtube.com/watch?v="

YDL_OPTS = {
    'format':'bestaudio/best',
    'quiet': True,
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}