import logging
import urllib.parse
from typing import List

from cogs.music.extractor import ExtractorFactory
from cogs.music.song import Song
from discord.ext import commands

_log = logging.getLogger(__name__)


class Search:
    "Methods: query"

    def is_url(self, url_string):
        try:
            # Attempt to parse the URL
            result = urllib.parse.urlparse(url_string)
            # Check if all parts are defined (excluding fragment)
            return all([result.scheme, result.netloc, result.path])
        except (ValueError, AttributeError):
            # If parsing fails, the string is not a URL
            return False

    def is_soundcloud(self, url: str):
        parsed_url = urllib.parse.urlparse(url)
        netloc = parsed_url.netloc
        domain = netloc.split(".")[0]
        return domain.lower() == "soundcloud"

    async def query(
        self, query: str, ctx: commands.Context, priority: bool = False
    ) -> List[Song] | None:

        extractors = ExtractorFactory()
        songs = []

        if self.is_url(query):
            if self.is_soundcloud(query):
                songs = await extractors.get_extractor("soundcloud").get_data(
                    query=query, ctx=ctx
                )
            else:
                is_playlist = "/playlist?" in query or "&list=" in query
                songs = await extractors.get_extractor("youtube").get_data(
                    query=query, ctx=ctx, is_playlist=is_playlist
                )
        else:
            songs = await extractors.get_extractor("soundcloud").get_data(
                query=query, ctx=ctx, is_search=True
            )
            if not songs:
                songs = await extractors.get_extractor("youtube").get_data(
                    query=query, ctx=ctx, is_search=True
                )

        if songs:
            if priority:
                songs.reverse()
            return [song for song in songs if song is not None]
        else:
            _log.error(f"No results were found for the query '{query}'")
            return None
