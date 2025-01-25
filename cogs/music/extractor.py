import asyncio
import logging
from abc import ABC, abstractmethod
from typing import List, Literal, Union

from cogs.music.core.song import (
    SongMeta,
    SoundCloudSongMeta,
    SpotifySongMeta,
    YouTubeSongMeta,
    format_duration,
)
from cogs.music.services.soundcloud.service import SoundCloudService
from cogs.music.services.spotify import album, playlist, search, track
from cogs.music.services.spotify.service import SpotifyService
from cogs.music.services.youtube.service import YouTubeService
from core.exceptions import ExtractException
from discord.ext import commands
from pytubefix import Playlist, Search, YouTube
from pytubefix.exceptions import VideoUnavailable
from soundcloud import BasicTrack, MiniTrack
from soundcloud.resource.track import Track

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
            results = Search(query, po_token_verifier=YouTubeService.getPoToken, use_po_token=True).videos
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
            playlist = Playlist(query, po_token_verifier=YouTubeService.getPoToken, use_po_token=True)
            songs = await asyncio.gather(
                *[
                    self.create_song_metadata(video, ctx, playlist.title)
                    for video in playlist.videos
                ]
            )
            return songs
        else:
            try:
                yt = YouTube(query, po_token_verifier=YouTubeService.getPoToken, use_po_token=True)

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


class SpotifyExtractor(Extractor):
    def __init__(self) -> None:
        super().__init__()
        self.sp = SpotifyService()

    async def create_song_metadata(
        self,
        data: Union[search.Track, playlist.Track, track.Track, album.Track],
        ctx,
        playlist_name,
    ) -> SpotifySongMeta:
        return SpotifySongMeta(
            title=data.name,
            duration=format_duration(data.duration_ms, unit="milliseconds"),
            track_id=data.id,
            ctx=ctx,
            playlist_name=playlist_name,
            webpage_url=data.external_urls.spotify,
            author=", ".join([artist.name for artist in data.artists]),
        )

    async def get_data(
        self,
        query: str,
        ctx: commands.Context,
        is_search: bool = False,
        is_playlist: bool = False,
        limit: int = 1,
    ) -> List[SpotifySongMeta] | None:
        if is_search:
            data = self.sp.search(query, limit=limit)
            songs = await asyncio.gather(
                *[self.create_song_metadata(track, ctx, None) for track in data.items]
            )
            return songs

        data = await self.sp.resolve_url(query)
        if isinstance(data, playlist.Playlist):
            playlist_name = data.name
            songs = await asyncio.gather(
                *[
                    self.create_song_metadata(track.track, ctx, playlist_name)
                    for track in data.tracks.items
                ]
            )
        elif isinstance(data, album.Album):
            playlist_name = data.name
            songs = await asyncio.gather(
                *[
                    self.create_song_metadata(track, ctx, playlist_name)
                    for track in data.tracks.items
                ]
            )
        elif isinstance(data, track.Track):
            songs = [await self.create_song_metadata(data, ctx, None)]
        return songs


class ExtractorFactory:
    extractors = {
        "youtube": YoutubeExtractor,
        "soundcloud": SoundCloudExtractor,
        "spotify": SpotifyExtractor,
    }

    @classmethod
    def get_extractor(
        cls, extractor: Literal["youtube", "soundcloud", "spotify"]
    ) -> Extractor:
        if extractor in cls.extractors:
            return cls.extractors[extractor]()
        else:
            raise ExtractException(f"Cannot find extractor with name '{extractor}'")
