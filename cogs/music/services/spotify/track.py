from dataclasses import dataclass
from typing import List, Dict
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
    is_playable: bool
    name: str
    popularity: int
    preview_url: str
    track_number: int
    type: str
    uri: str


def load_track(json_data: dict) -> Track:
    """Factory function to load track from JSON"""
    return Track.from_dict(json_data)  # type: ignore
