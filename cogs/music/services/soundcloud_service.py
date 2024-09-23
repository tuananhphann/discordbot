from soundcloud import AlbumPlaylist, SoundCloud, Track
from soundcloud.resource.base import BaseData
import requests
from dataclasses import dataclass
from cogs.music.exceptions import ResolveException


@dataclass(slots=True)
class TrackPlayable(BaseData):
    """Provide a playback URL of a Track"""

    url: str


class SoundCloudService:
    def __init__(self) -> None:
        self.sc = SoundCloud()
        self.client_id = self.sc.client_id

    def search(self, query: str):
        return self.sc.search(query)

    def resolve_url(self, url: str):
        return self.sc.resolve(url)

    def get_thumbnail(self, track: Track) -> str:
        return track.artwork_url or track.user.avatar_url

    def get_playback_url(self, track: Track):
        # Transcoding involves 3 types of protocols: HLS, progressive and Opus.
        # We prefer to use the 'HLS' protocol because it's the best for streaming.
        stream_url = track.media.transcodings[0].url
        track_authorization = track.track_authorization
        params = {
            "client_id": self.client_id,
            "track_authorization": track_authorization,
        }
        response = requests.get(
            stream_url, headers=self.sc._get_default_headers(), params=params
        )
        return TrackPlayable.from_dict(response.json())

    def extract_song_from_url(self, url: str):
        resolve = self.resolve_url(url)
        if resolve is None or not isinstance(resolve, (AlbumPlaylist, Track)):
            if resolve is None:
                raise ResolveException(f"Cannot resolve the URL: {url}.")
            else:
                raise ResolveException(f"Cannot resolve the URL: {url}. Because it's not a track or playlist.")

        if isinstance(resolve, AlbumPlaylist):
            return {
                "playlist_id": resolve.id,
                "playlist_name": resolve.title,
                "tracks": resolve.tracks,
            }
        elif isinstance(resolve, Track):
            return {
                "playlist_id": None,
                "playlist_name": None,
                "tracks": [resolve],
            }
        else:
            return None
