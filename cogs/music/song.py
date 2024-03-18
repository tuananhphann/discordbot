from dataclasses import dataclass
from typing import Any, Dict

from discord.ext import commands

from .album import Album


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
    playback_url: str | tuple
    uploader: str
    playback_count: str
    duration: str
    upload_date: str
    thumbnail: str
    webpage_url: str
    album: Album | None
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
