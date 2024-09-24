from soundcloud import AlbumPlaylist, SoundCloud, Track
from soundcloud.resource.base import BaseData
import requests
from dataclasses import dataclass
from cogs.music.exceptions import ResolveException
from patterns.singleton import SingletonMeta
from utils.utils import to_thread
import logging

_log = logging.getLogger(__name__)


@dataclass(slots=True)
class TrackPlayable(BaseData):
    """Provide a playback URL of a Track"""

    url: str


class SoundCloudService(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self.sc = SoundCloud()
        self.client_id = self.sc.client_id

    def search(self, query: str):
        _log.info(f"Searching for: '{query}'")
        return self.sc.search(query)

    def resolve_url(self, url: str):
        _log.info(f"Resolving URL: '{url}'")
        return self.sc.resolve(url)

    def get_thumbnail(self, track: Track) -> str:
        return track.artwork_url or track.user.avatar_url

    @to_thread
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
        _log.info(f"Got playback URL for: '{track.title}'")
        return TrackPlayable.from_dict(response.json()).url

    async def extract_song_from_url(self, url: str):
        resolve = self.resolve_url(url)
        if resolve is None or not isinstance(resolve, (AlbumPlaylist, Track)):
            if resolve is None:
                error = f"Cannot resolve the URL: '{url}'."
                _log.error(error)
                raise ResolveException(error)
            else:
                error = f"Resolve type is {type(resolve)}. Expected type is Track or AlbumPlaylist."
                _log.error(error)
                raise ResolveException(error)

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
