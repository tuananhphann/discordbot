import datetime
# from album import Album
from typing import Any, Dict

import requests
from fake_useragent import FakeUserAgent

from .errors import MusicError
from .song import Album, Song

ua = FakeUserAgent()
session = requests.session()
client_id = "LBCcHmRB8XSStWL6wKH2HPACspQlXg2P"
song_url = "https://soundcloud.com/rapviet_viechannel/rolling-down-feat-captain"
playlist_url = "https://soundcloud.com/rapviet_viechannel/sets/rap-vi-t-2023-t-p-13"
album_url = "https://soundcloud.com/user-443192601/sets/nhac-phim-mua-viet-tinh-ca"


headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Host": "api-widget.soundcloud.com",
    "User-Agent": ua.random
}


def resolve_url(url: str) -> Dict[str, Any]:
    res = session.get(url, headers=headers)
    if res.status_code == 200:
        return res.json()
    else:
        raise MusicError("SoundCloud: Cannot resolve the given URL.")


def get_playback_url(track: Dict[str, Any]):
    stream_url = track["media"]["transcodings"][0]["url"]
    track_authorization = track["track_authorization"]
    audio_url = f"{stream_url}?client_id={client_id}&track_authorization={track_authorization}"

    # Transcoding involves 3 types of protocols: HLS, progressive and Opus.
    # We prefer to use the 'HLS' protocol
    response = session.get(url=audio_url, headers=headers)
    playback_url = response.json()
    return playback_url["url"]
    # return audio_url


# The response data will be in one of the following forms: 'track' or 'playlist'.
# Additionally, the term 'playlist' also encompasses albums.
# The specific format of the response data will determine the type of responsive function we need to create.
def format_duration(duration):
    duration_fmt = datetime.timedelta(milliseconds=float(duration))
    formatted_duration = str(duration_fmt - datetime.timedelta(microseconds=duration_fmt.microseconds))
    return formatted_duration


def format_playback_count(playback_count) -> str:
    view_count_fmt = int(playback_count)
    return "{:,}".format(view_count_fmt)


def format_upload_date(date):
    datetime_obj = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
    return datetime_obj.strftime("%d/%m/%Y")


def get_thumbnail(track):
    if track["artwork_url"] is None:
        thumbnail = track["user"]["avatar_url"]
    else:
        thumbnail = track["artwork_url"]

    return thumbnail


def get_data(soundcloud_url, ctx):
    url = f"https://api-widget.soundcloud.com/resolve?url={soundcloud_url}&format=json&client_id=LBCcHmRB8XSStWL6wKH2HPACspQlXg2P&app_version=1692966083"
    response_data = resolve_url(url)
    kind = response_data["kind"]
    if kind == "track":
        track = response_data
        song = Song(
            title=track["title"],
            playback_url=get_playback_url(track),
            uploader=track["user"]["username"],
            duration=format_duration(track["duration"]),
            playback_count=format_playback_count(track["playback_count"]),
            upload_date=format_upload_date(track["created_at"]),
            thumbnail=get_thumbnail(track),
            webpage_url=track["permalink_url"],
            category=track["genre"],
            album=None,
            context=ctx
        )
        return song
    else:
        playlist_id = response_data["id"]
        track_ids = ",".join([str(track["id"]) for track in response_data["tracks"]])
        playlist_name = response_data["title"]
        get_track_url = f"https://api-widget.soundcloud.com/tracks?ids={track_ids}&playlistId={playlist_id}&playlistSecretToken&format=json&client_id={client_id}"
        response = session.get(get_track_url, headers=headers)
        tracks = response.json()

        songs = [Song(
                title=track["title"],
                playback_url=get_playback_url(track),
                uploader=track["user"]["username"],
                duration=format_duration(track["duration"]),
                playback_count=format_playback_count(track["playback_count"]),
                upload_date=format_upload_date(track["created_at"]),
                thumbnail=get_thumbnail(track),
                webpage_url=track["permalink_url"],
                category=track["genre"],
                album=Album(playlist_name),
                context=ctx
            )
            for track in tracks
        ]
        return songs

# data = get_data()
# if isinstance(data, list):
#     for song in data:
#         print(song)
# else:
#     print(data)
