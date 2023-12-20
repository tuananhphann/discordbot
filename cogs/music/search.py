import asyncio
import datetime
import logging
from urllib.parse import urlparse

import yt_dlp as youtube_dl
from discord.ext import commands
from requests import get

import constants
from cogs.music.song import Song

from .soundcloud import get_data

_log = logging.getLogger(__name__)


class Search:
    "Methods: query"

    def __init__(self):
        self.__ydl = youtube_dl.YoutubeDL(constants.YDL_OPTS)

    def __format_upload_date(self, upload_date: str) -> str:
        date = datetime.datetime.strptime(
            upload_date[:4] + "/" + upload_date[4:6] + "/" + upload_date[6:], "%Y/%m/%d"
        )
        date = date.strftime("%d/%m/%Y")
        return date

    def __format_duration(self, duration: str) -> str:
        duration_fmt = datetime.timedelta(seconds=float(duration))
        return str(duration_fmt)

    def __format_view_count(self, view_count: str) -> str:
        view_count_fmt = int(view_count)
        return "{:,}".format(view_count_fmt)

    def is_soundcloud(self, url: str):
        parsed_url = urlparse(url)
        netloc = parsed_url.netloc
        domain = netloc.split(".")[0]
        if domain.lower() == "soundcloud":
            return True
        else:
            return False

    async def query(self, query: str, ctx: commands.Context) -> Song | list[Song]:
        """Search by a name or URL.

        If success, return Song, else, return -1

        return:
            Song object
        or  int: -1"""
        loop = asyncio.get_event_loop()
        _log.info(f"Searching for '{query}'.")

        try:
            get(query)
        except:
            try:
                video = await loop.run_in_executor(
                    None,
                    lambda: self.__ydl.extract_info(
                        f"ytsearch:{query}", download=False
                    )["entries"][0],
                )
                _log.info(f"Extract info from '{query}' successfully.")
            except Exception as e:
                _log.error(e)
                return -1
        else:
            try:
                if self.is_soundcloud(query):
                    print("Detected soundcloud URL")
                    return get_data(query, ctx)
                else:
                    video = await loop.run_in_executor(
                        None, lambda: self.__ydl.extract_info(query, download=False)
                    )
            except Exception as e:
                _log.error(e)
                return -1

        song = Song(
            title=video["title"],
            playback_url=video["url"],
            uploader=video["channel"],
            playback_count=self.__format_view_count(video["view_count"]),
            duration=self.__format_duration(video["duration"]),
            upload_date=self.__format_upload_date(video["upload_date"]),
            thumbnail=video["thumbnail"],
            webpage_url=video["webpage_url"],
            category=video["categories"][0],
            album=None,
            context=ctx,
        )

        return song
