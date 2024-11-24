from dataclasses import dataclass
from typing import List, Dict, Optional
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
    width: int
    height: int


@dataclass
class Album(JsonObject):
    album_type: str
    artists: List[Artist]
    external_urls: ExternalUrls
    href: str
    id: str
    images: List[Image]
    is_playable: bool
    name: str
    release_date: str
    release_date_precision: str
    total_tracks: int
    type: str
    uri: str


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


def load_search(json_data: dict) -> Tracks:
    """Factory function to load search results from a dictionary."""
    return Tracks.from_dict(json_data)  # type: ignore
