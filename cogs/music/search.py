import logging
import urllib.parse
from typing import List, Optional
from discord.ext import commands

from cogs.music.extractor import ExtractorFactory
from cogs.music.core.song import SongMeta

_log = logging.getLogger(__name__)


class Search:
    "Methods: query"

    def is_url(self, url_string: str) -> bool:
        try:
            # Attempt to parse the URL
            result = urllib.parse.urlparse(url_string)
            # Check if all parts are defined (excluding fragment)
            return all([result.scheme, result.netloc, result.path])
        except (ValueError, AttributeError):
            # If parsing fails, the string is not a URL
            return False

    def is_soundcloud(self, url: str) -> bool:
        parsed_url = urllib.parse.urlparse(url)
        netloc = parsed_url.netloc
        domain = netloc.split(".")[0]
        return domain.lower() == "soundcloud"

    async def query(self, query: str, ctx: commands.Context, priority: bool = False) -> Optional[List[SongMeta]]:
        """
        Queries the provided string to fetch song metadata from either YouTube or SoundCloud.

        If the query is a URL, it determines whether it is a SoundCloud or YouTube link and fetches the data
        accordingly.

        If the query is not a URL, it first attempts to search SoundCloud, and if no results are found, it searches
        YouTube.
        Args:
            query (str): The search string or URL to query.
            ctx (commands.Context): The context in which the command was invoked.
            priority (bool, optional): If True, the order of the songs will be reversed. Defaults to False.
        Returns:
            List[SongMeta] | None: A list of SongMeta objects if songs are found, otherwise None.
        """
        songs = []

        if self.is_url(query):
            if self.is_soundcloud(query):
                songs = await ExtractorFactory.get_extractor("soundcloud").get_data(
                    query=query, ctx=ctx
                )
            else:
                is_playlist = "/playlist?" in query or "&list=" in query
                songs = await ExtractorFactory.get_extractor("youtube").get_data(
                    query=query, ctx=ctx, is_playlist=is_playlist
                )
        else:
            songs = await ExtractorFactory.get_extractor("soundcloud").get_data(
                query=query, ctx=ctx, is_search=True
            )
            if not songs:
                songs = await ExtractorFactory.get_extractor("youtube").get_data(
                    query=query, ctx=ctx, is_search=True
                )

        if songs:
            if priority:
                songs.reverse()
            return [song for song in songs if song is not None]
        else:
            _log.error(f"No results were found for the query '{query}'")
            return None
