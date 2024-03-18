import asyncio
import datetime
import logging
from abc import ABC, abstractmethod
from typing import List

import constants
import yt_dlp as youtube_dl
from cogs.music.album import Album
from cogs.music.song import Song
from cogs.music.soundcloud import SoundCloud
from pytube import Playlist, Search, YouTube
from pytube.exceptions import VideoUnavailable
from utils.http_request import HttpRequest

_log = logging.getLogger(__name__)


class Extractor(ABC):
    def __init__(self) -> None:
        self.requester = HttpRequest()
        self.loop = asyncio.get_event_loop()
        self._ydl = youtube_dl.YoutubeDL(constants.YDL_OPTS)

    @abstractmethod
    async def get_data(self, query, ctx, is_search=False, is_playlist=False) -> List[Song] | None:
        pass


class YoutubeExtractor(Extractor):
    def format_duration(self, duration: int) -> str:
        duration_fmt = datetime.timedelta(seconds=float(duration))
        return str(duration_fmt)

    def format_view_count(self, view_count: int) -> str:
        return "{:,}".format(view_count)

    def format_upload_date(self, upload_date: datetime.datetime) -> str:
        date = upload_date.strftime("%d/%m/%Y")
        return date

    def get_playback_url(self, yt: YouTube) -> str:
        return yt.streams.get_audio_only().url

    async def get_data(self, query: str, ctx, is_search=False, is_playlist=False) -> List[Song] | None:
        if is_search:
            results = Search(query).results
            if results is not None:
                result = results[0]
                song = Song(
                    title=result.title,
                    playback_url=(self.get_playback_url, result),
                    uploader=result.author,
                    playback_count=self.format_view_count(result.views),
                    duration=self.format_duration(result.length),
                    upload_date=self.format_upload_date(result.publish_date),
                    thumbnail=result.thumbnail_url,
                    webpage_url=result.watch_url,
                    album=None,
                    context=ctx,
                )
                return [song]
            else:
                return None
        elif is_playlist:
            playlist = Playlist(query)
            songs = []
            for video in playlist.videos:
                song = Song(
                    title=video.title,
                    playback_url=(self.get_playback_url, video),
                    uploader=video.author,
                    playback_count=self.format_view_count(video.views),
                    duration=self.format_duration(video.length),
                    upload_date=self.format_upload_date(video.publish_date),
                    thumbnail=video.thumbnail_url,
                    webpage_url=video.watch_url,
                    album=Album(playlist.title),
                    context=ctx,
                )
                songs.append(song)
            return songs
        else:
            try:
                yt = YouTube(query)
            except VideoUnavailable:
                return None

            song = Song(
                title=yt.title,
                playback_url=yt.streams.get_audio_only().url,
                uploader=yt.author,
                playback_count=self.format_view_count(yt.views),
                duration=self.format_duration(yt.length),
                upload_date=self.format_upload_date(yt.publish_date),
                thumbnail=yt.thumbnail_url,
                webpage_url=yt.watch_url,
                album=None,
                context=ctx,
            )
            return [song]


class SoundCloudExtractor(Extractor):
    def __init__(self) -> None:
        super().__init__()
        self.soundcloud = SoundCloud()

    def format_duration(self, duration) -> str:
        duration_fmt = datetime.timedelta(milliseconds=float(duration))
        return str(
            duration_fmt - datetime.timedelta(microseconds=duration_fmt.microseconds)
        )

    def format_playback_count(self, playback_count) -> str:
        return f"{int(playback_count):,}"

    def format_upload_date(self, date) -> str:
        return datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ").strftime(
            "%d/%m/%Y"
        )

    async def create_song(self, track, ctx, playlist_name) -> Song:
        return Song(
            title=track["title"],
            playback_url=(self.soundcloud.get_playback_url, track),
            uploader=track["user"]["username"],
            duration=self.format_duration(track["duration"]),
            playback_count=self.format_playback_count(track["playback_count"]),
            upload_date=self.format_upload_date(track["created_at"]),
            thumbnail=self.soundcloud.get_thumbnail(track),
            webpage_url=track["permalink_url"],
            album=Album(playlist_name) if playlist_name is not None else None,
            context=ctx,
        )

    async def get_data(self, query, ctx, is_search=False) -> List[Song] | None:
        if is_search:
            data = self.soundcloud.search(query)
            tracks = data["tracks"][0]
            song = await self.create_song(tracks, ctx, None)
            return [song]

        data = await self.soundcloud.extract_song(query)
        playlist_name = data["playlist_name"]
        tracks = data["tracks"]
        songs = await asyncio.gather(*[self.create_song(track, ctx, playlist_name) for track in tracks])
        return songs


class ExtractorFactory:
    extractors = {"youtube": YoutubeExtractor, "soundcloud": SoundCloudExtractor}

    def get_extractor(self, extractor: str) -> Extractor:
        if extractor in self.extractors:
            return self.extractors[extractor]()
        else:
            raise Exception(f"Cannot find extractor with name '{extractor}'")
