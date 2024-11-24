import urllib.parse

import spotipy
from cogs.music.services.spotify.album import Album, load_album
from cogs.music.services.spotify.playlist import Playlist, load_playlist
from cogs.music.services.spotify.search import load_search
from cogs.music.services.spotify.spotify_type import SpotifyType
from cogs.music.services.spotify.track import Track, load_track
from patterns.singleton import SingletonMeta
from spotipy.oauth2 import SpotifyClientCredentials


class SpotifyService(metaclass=SingletonMeta):

    def __init__(self, market: str = "VN", language: str = "vi") -> None:
        self.auth_manager = SpotifyClientCredentials()
        self.sp = spotipy.Spotify(auth_manager=self.auth_manager)
        self.market = market
        self.language = language

    def __get_type(self, url: str):
        path = urllib.parse.urlparse(url).path
        path = path.split("/")
        return path[1]

    def __resolve_album(self, url: str) -> Album:
        album = self.sp.album(url, market=self.market)
        return load_album(album)  # type: ignore

    def __resolve_track(self, url: str) -> Track:
        track = self.sp.track(url, market=self.market)
        return load_track(track)  # type: ignore

    def __resolve_playlist(self, url: str) -> Playlist:
        playlist = self.sp.playlist(url, market=self.market)
        return load_playlist(playlist)  # type: ignore

    async def resolve_url(self, url: str):
        type_ = self.__get_type(url)
        if type_ == SpotifyType.ALBUM.value:
            return self.__resolve_album(url)
        elif type_ == SpotifyType.TRACK.value:
            return self.__resolve_track(url)
        elif type_ == SpotifyType.PLAYLIST.value:
            return self.__resolve_playlist(url)
        else:
            raise ValueError(f"Invalid Spotify URL: {url}")

    def get_track(self, track_id: str) -> Track:
        track = self.sp.track(track_id, market=self.market)
        return load_track(track)  # type: ignore

    def get_album(self, album_id: str) -> Album:
        album = self.sp.album(album_id, market=self.market)
        return load_album(album)  # type: ignore

    def get_playlist(self, playlist_id: str) -> Playlist:
        playlist = self.sp.playlist(playlist_id, market=self.market)
        return load_playlist(playlist)  # type: ignore

    def search(
        self, query: str, type_: str = SpotifyType.TRACK.value, limit: int = 1
    ):
        search = self.sp.search(query, limit=limit, type=type_, market=self.market)
        return load_search(search)  # type: ignore

    # async def get_playback_url(self, track: Track) -> str:
    #     result = await ExtractorFactory.get_extractor("youtube").get_data(track.name, None, True, 1)
    #     return result[0].
