from discord.ext import commands
from .album import Album
from typing import Any


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
    - context (commands.Context | None): The context in which the song is being used (if applicable).

    Methods:
    - __str__(): Returns a formatted string representation of the song's details.
    - info(): Returns a dictionary containing the song's information.
    """

    def __init__(
        self,
        title: str,
        playback_url: str,
        uploader: str,
        playback_count: str,
        duration: str,
        upload_date: str,
        thumbnail: str,
        webpage_url: str,
        category: str,
        album: Album | None,
        context: commands.Context,
    ) -> None:
        self.title: str = title
        self.playback_url: str = playback_url
        self.uploader: str = uploader
        self.playback_count: str = playback_count
        self.duration: str = duration
        self.upload_date: str = upload_date
        self.thumbnail: str = thumbnail
        self.webpage_url: str = webpage_url
        self.category: str = category
        self.album = album
        self.context = context

    def __str__(self) -> str:
        return f"""
        [{self.title}]({self.webpage_url})
        Uploader: {self.uploader}
        Playback counts: {self.playback_count}
        Duration: {self.duration}
        Upload date: {self.upload_date}
        Category: {self.category}
        Album: {self.album.title if self.album else None}
        """

    def info(self) -> dict[str, Any]:
        """
        Return a dictionary containing the song's information.
        """
        song: dict[str, Any] = {
            "title": self.title,
            "playback_url": self.playback_url,
            "uploader": self.uploader,
            "playback_count": self.playback_count,
            "duration": self.duration,
            "upload_date": self.upload_date,
            "thumbnail": self.thumbnail,
            "webpage_url": self.webpage_url,
            "category": self.category,
            "album": self.album,
        }
        return song
