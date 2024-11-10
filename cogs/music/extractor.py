import asyncio
import logging
from abc import ABC, abstractmethod
from typing import List, Literal, Union

from discord.ext import commands
from pytubefix import Playlist, Search, YouTube
from pytubefix.exceptions import VideoUnavailable
from soundcloud import BasicTrack, MiniTrack
from soundcloud.resource.track import Track

from core.exceptions import ExtractException
from cogs.music.services.soundcloud_service import SoundCloudService
from cogs.music.core.song import (
    SongMeta,
    SoundCloudSongMeta,
    YouTubeSongMeta,
    format_duration,
)

_log = logging.getLogger(__name__)


class Extractor(ABC):
    def __init__(self) -> None:
        self.loop = asyncio.get_event_loop()

    @abstractmethod
    async def create_song_metadata(self, data, ctx, playlist_name) -> SongMeta:
        pass

    @abstractmethod
    async def get_data(
        self,
        query: str,
        ctx: commands.Context,
        is_search: bool = False,
        is_playlist: bool = False,
        limit: int = 1,
    ) -> List[SongMeta] | None:
        pass


class YoutubeExtractor(Extractor):
    def __init__(self) -> None:
        super().__init__()

    async def create_song_metadata(
        self, yt: YouTube, ctx: commands.Context, playlist_name: str | None
    ) -> YouTubeSongMeta:
        return YouTubeSongMeta(
            title=yt.title,
            duration=format_duration(yt.length),
            video_id=yt.video_id,
            ctx=ctx,
            playlist_name=playlist_name,
            webpage_url=yt.watch_url,
            author=yt.author,
        )

    async def get_data(
        self, query: str, ctx, is_search=False, is_playlist=False, limit=1
    ) -> List[YouTubeSongMeta] | None:
        if is_search:
            results = Search(query).videos
            if results:
                songs = await asyncio.gather(
                    *[
                        self.create_song_metadata(result, ctx, None)
                        for result in results[:limit]
                    ]
                )
                return songs
            return None

        if is_playlist:
            playlist = Playlist(query)
            songs = await asyncio.gather(
                *[
                    self.create_song_metadata(video, ctx, playlist.title)
                    for video in playlist.videos
                ]
            )
            return songs
        else:
            try:
                yt = YouTube(query)
            except VideoUnavailable:
                return None

            song = await self.create_song_metadata(yt, ctx, None)
            return [song]


class SoundCloudExtractor(Extractor):
    def __init__(self) -> None:
        super().__init__()
        self.soundcloud = SoundCloudService()

    async def create_song_metadata(
        self,
        track: Union[Track, BasicTrack, MiniTrack],
        ctx: commands.Context,
        playlist_name: str | None,
    ) -> SoundCloudSongMeta:
        return SoundCloudSongMeta(
            title=track.title if not isinstance(track, MiniTrack) else None,
            duration=(
                format_duration(track.duration, unit="milliseconds")
                if not isinstance(track, MiniTrack)
                else "0"
            ),
            track_id=track.id,
            ctx=ctx,
            playlist_name=playlist_name,
            webpage_url=(
                track.permalink_url if not isinstance(track, MiniTrack) else None
            ),
            author=(
                track.user.username if not isinstance(track, MiniTrack) else "Unknown"
            ),
        )

    async def get_data(
        self, query, ctx, is_search=False, limit=1
    ) -> List[SoundCloudSongMeta] | None:
        if is_search:
            data = await self.soundcloud.search(query)
            tracks = []
            for _ in range(limit):
                track = next(data)
                while not isinstance(track, (Track, BasicTrack)):
                    track = next(data)
                tracks.append(track)

            songs = await asyncio.gather(
                *[self.create_song_metadata(track, ctx, None) for track in tracks]
            )

            return songs

        data = await self.soundcloud.extract_song_from_url(query)

        if data is None:
            raise ExtractException("Failed to extract song from SoundCloud URL")

        playlist_name = data["playlist_name"]
        tracks = data["tracks"]
        songs = await asyncio.gather(
            *[self.create_song_metadata(track, ctx, playlist_name) for track in tracks]
        )
        _log.info(f"Extracted {len(songs)} song(s) from SoundCloud URL.")
        return songs


class ExtractorFactory:
    extractors = {"youtube": YoutubeExtractor, "soundcloud": SoundCloudExtractor}

    @classmethod
    def get_extractor(cls, extractor: Literal["youtube", "soundcloud"]) -> Extractor:
        if extractor in cls.extractors:
            return cls.extractors[extractor]()
        else:
            raise ExtractException(f"Cannot find extractor with name '{extractor}'")
