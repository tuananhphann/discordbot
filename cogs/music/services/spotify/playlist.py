from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from mapper.jsonmapper import JsonObject


@dataclass
class ExternalUrls(JsonObject):
    spotify: str


@dataclass
class Image(JsonObject):
    height: Optional[int]
    url: str
    width: Optional[int]


@dataclass
class Owner(JsonObject):
    display_name: str
    external_urls: ExternalUrls
    href: str
    id: str
    type: str
    uri: str


@dataclass
class Artist(JsonObject):
    external_urls: ExternalUrls
    href: str
    id: str
    name: str
    type: str
    uri: str


@dataclass
class Album(JsonObject):
    album_type: str
    artists: List[Artist]
    external_urls: ExternalUrls
    href: str
    id: str
    images: List[Image]
    name: str
    release_date: str
    release_date_precision: str
    total_tracks: int
    type: str
    uri: str
    is_playable: bool = True


@dataclass
class Track(JsonObject):
    album: Album
    artists: List[Artist]
    disc_number: int
    duration_ms: int
    explicit: bool
    external_ids: Dict[str, str]
    external_urls: ExternalUrls
    href: str
    id: str
    is_local: bool
    name: str
    popularity: int
    preview_url: Optional[str]
    track_number: int
    type: str
    uri: str
    is_playable: bool = True
    track: bool = True
    episode: bool = False


@dataclass
class TrackItem(JsonObject):
    added_at: str
    added_by: Dict[str, str]
    is_local: bool
    primary_color: Optional[str]
    track: Track
    video_thumbnail: Dict[str, Optional[str]]


@dataclass
class Tracks(JsonObject):
    href: str
    items: List[TrackItem]
    limit: int
    next: Optional[str]
    offset: int
    previous: Optional[str]
    total: int


@dataclass
class Playlist(JsonObject):
    collaborative: bool
    description: str
    external_urls: ExternalUrls
    followers: Dict[str, Any]
    href: str
    id: str
    images: List[Image]
    name: str
    owner: Owner
    primary_color: str
    public: bool
    snapshot_id: str
    tracks: Tracks
    type: str
    uri: str


def load_playlist(json_data: dict) -> Playlist:
    """Factory function to load playlist from JSON"""
    return Playlist.from_dict(json_data)  # type: ignore
