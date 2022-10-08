import asyncio
import datetime

import constants
import youtube_dl
from cogs.music.song import Song
from requests import get
from youtube_search import YoutubeSearch


class Search:
    "Methods: query"

    def __init__(self):
        self.__ydl = youtube_dl.YoutubeDL(constants.YDL_OPTS)

    def __search_name(self, name: str):
        """Searching on Youtube by song name, returns the video URL of that song on Youtube."""
        r = YoutubeSearch(search_terms=name, max_results=1).to_dict()
        r = r[0]  # get first result
        return constants.YOUTUBE_PREFIX + r['url_suffix']

    def __format_upload_date(self, upload_date: str) -> str:
        return upload_date[:4] + "/" + upload_date[4:6] + "/" + upload_date[6:]

    def __format_duration(self, duration: str) -> str:
        return str(datetime.timedelta(seconds=duration))

    def __format_view_count(self, view_count: str) -> str:
        view_count = int(view_count)
        return "{:,}".format(view_count)

    async def query(self, query: str) -> Song:
        """Search by a name or URL
        
        return: Song object"""
        loop = asyncio.get_event_loop()
        
        try:
            get(query) 
        except:
            video = await loop.run_in_executor(None, lambda: self.__ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0])
        else:
            video = await loop.run_in_executor(None, lambda: self.__ydl.extract_info(query, download=False))
                
        song = Song(
            video['title'],
            video['url'],
            video['channel'],
            self.__format_view_count(video['view_count']),
            self.__format_duration(video['duration']),
            self.__format_upload_date(video['upload_date']),
            video['thumbnail'],
            video['webpage_url'])

        return song
