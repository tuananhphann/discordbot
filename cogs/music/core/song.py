from dataclasses import dataclass
from functools import singledispatch
from typing import Any, Dict, List, Union, Optional

from discord.ext import commands
from pytube import YouTube
from pytube.exceptions import VideoUnavailable
from soundcloud import BasicTrack, Track

from cogs.music.core.album import Album
from cogs.music.services.soundcloud_service import SoundCloudService
from utils import format_duration, format_playback_count, safe_format_date, safe_getattr


@dataclass(slots=True)
class Song:
    """
    Represents a song with various attributes and methods to access its information.

    Parameters:
    - title (str): The title of the song.
    - playback_url (str): The URL to play the song.
    - uploader (str): The name of the uploader.
    - playback_count (str): The number of times the song has been played.
    - duration (str): The duration of the song.
    - upload_date (str): The date when the song was uploaded.
    - thumbnail (str): The URL to the thumbnail image of the song.
    - webpage_url (str): The URL to the webpage of the song.
    - category (str): The category of the song.
    - album (Album): Song's album
    - context (commands.Context | None): The context in which the song is being used (if applicable).

    Methods:
    - info(): Returns a dictionary containing the song's information.
    """

    title: str
    playback_url: Optional[str]
    uploader: str
    playback_count: str
    duration: str
    upload_date: str
    thumbnail: str
    webpage_url: str
    album: Optional['Album']
    context: commands.Context

    def info(self) -> Dict[str, Any]:
        """
        Return a dictionary containing the song's information.
        """
        song: Dict[str, Any] = {
            "title": self.title,
            "playback_url": self.playback_url,
            "uploader": self.uploader,
            "playback_count": self.playback_count,
            "duration": self.duration,
            "upload_date": self.upload_date,
            "thumbnail": self.thumbnail,
            "webpage_url": self.webpage_url,
            "album": self.album,
        }
        return song


@dataclass(slots=True)
class SongMeta:
    """
    Represents a song metadata, contains data used for extract a song's information.
    Mainly used for song queue, before the song was loaded.
    """

    title: str | None
    duration: str
    playlist_name: str | None
    webpage_url: str | None
    ctx: commands.Context

    def update_meta(self, *args, **kwargs) -> None:
        """This method updates the metadata of the song with the given video information.
        The following attributes will be updated:
        - title
        - duration
        - webpage_url
        """
        raise NotImplementedError("This method must be implemented in a subclass.")


@dataclass(slots=True)
class YouTubeSongMeta(SongMeta):
    """
    Represents a song metadata for YouTube, contains data used for extract a song's information.
    Mainly used for song queue, before the song was loaded.
    """

    video_id: str

    def update_meta(self, video: YouTube) -> None:
        self.title = video.title
        self.duration = format_duration(video.length)
        self.webpage_url = video.watch_url


@dataclass(slots=True)
class SoundCloudSongMeta(SongMeta):
    """
    Represents a song metadata for SoundCloud, contains data used for extract a song's information.
    Mainly used for song queue, before the song was loaded.
    """

    track_id: int

    def update_meta(self, track: Union[Track, BasicTrack]) -> None:
        self.title = track.title
        self.duration = format_duration(track.duration, unit="milliseconds")
        self.webpage_url = track.permalink_url


@singledispatch
async def createSong(song_meta: SongMeta) -> Union[Song, None]:
    raise NotImplementedError(f"Cannot create song from {type(song_meta)}")


@createSong.register  # type: ignore
async def _(song_meta: YouTubeSongMeta) -> Union[Song, None]:
    video = YouTube.from_id(song_meta.video_id)
    try:
        video.check_availability()
    except VideoUnavailable:
        return None
    playback_url = video.streams.get_audio_only().url

    return Song(
        title=video.title,
        playback_url=playback_url,
        uploader=video.author,
        playback_count=format_playback_count(video.views),
        duration=song_meta.duration,
        upload_date=safe_format_date(video.publish_date),
        thumbnail=video.thumbnail_url,
        webpage_url=video.watch_url,
        album=Album(song_meta.playlist_name) if song_meta.playlist_name else None,
        context=song_meta.ctx,
    )


@createSong.register  # type: ignore
async def _(song_meta: SoundCloudSongMeta) -> Union[Song, None]:
    sc_service = SoundCloudService()

    track = sc_service.sc.get_track(song_meta.track_id)
    if track is None:
        return None
    playback_url = await sc_service.get_playback_url(track)

    return Song(
        title=track.title,
        playback_url=playback_url,
        uploader=track.user.username,
        duration=song_meta.duration,
        playback_count=format_playback_count(safe_getattr(track, "playback_count", 0)),
        upload_date=safe_format_date(track.created_at),
        thumbnail=sc_service.get_thumbnail(track),
        webpage_url=track.permalink_url,
        album=Album(song_meta.playlist_name) if song_meta.playlist_name else None,
        context=song_meta.ctx,
    )


async def get_songs_info(songs_need_to_update: List[SongMeta]) -> List[SongMeta]:
    sc_songs: List[SoundCloudSongMeta] = []
    yt_songs: List[YouTubeSongMeta] = []

    # Separate songs by their type
    for song in songs_need_to_update:
        if isinstance(song, SoundCloudSongMeta):
            sc_songs.append(song)
        elif isinstance(song, YouTubeSongMeta):
            yt_songs.append(song)

    # Get YouTube info
    for song in yt_songs:
        video = YouTube.from_id(song.video_id)
        song.update_meta(video)

    # Get SoundCloud info
    sc_service = SoundCloudService()
    tracks = await sc_service.get_tracks_info([song.track_id for song in sc_songs])
    for track in tracks:
        song = next((s for s in sc_songs if s.track_id == track.id), None)
        if song:
            song.update_meta(track)

    # Merge all songs back to the original list
    for song in songs_need_to_update:
        if isinstance(song, SoundCloudSongMeta):
            song = next((s for s in sc_songs if s.track_id == song.track_id), song)
        elif isinstance(song, YouTubeSongMeta):
            song = next((s for s in yt_songs if s.video_id == song.video_id), song)

    return songs_need_to_update
