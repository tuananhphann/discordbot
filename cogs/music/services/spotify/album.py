from dataclasses import dataclass
from typing import List, Optional, Dict
from mapper.jsonmapper import JsonObject


@dataclass
class ExternalUrls(JsonObject):
    spotify: str


@dataclass
class Artist(JsonObject):
    external_urls: ExternalUrls
    href: str
    id: str
    name: str
    type: str
    uri: str


@dataclass
class Image(JsonObject):
    url: str
    height: int
    width: int


@dataclass
class Copyright(JsonObject):
    text: str
    type: str


@dataclass
class Track(JsonObject):
    artists: List[Artist]
    disc_number: int
    duration_ms: int
    explicit: bool
    external_urls: ExternalUrls
    href: str
    id: str
    is_local: bool
    is_playable: bool
    name: str
    preview_url: str
    track_number: int
    type: str
    uri: str


@dataclass
class Tracks(JsonObject):
    href: str
    limit: int
    next: Optional[str]
    offset: int
    previous: Optional[str]
    total: int
    items: List[Track]


@dataclass
class Album(JsonObject):
    album_type: str
    total_tracks: int
    is_playable: bool
    external_urls: ExternalUrls
    href: str
    id: str
    images: List[Image]
    name: str
    release_date: str
    release_date_precision: str
    type: str
    uri: str
    artists: List[Artist]
    tracks: Tracks
    copyrights: List[Copyright]
    external_ids: Dict[str, str]
    genres: List[str]
    label: str
    popularity: int


def load_album(json_data: dict) -> Album:
    """Factory function to load album from JSON"""
    return Album.from_dict(json_data)  # type: ignore
