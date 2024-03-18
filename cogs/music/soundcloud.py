import asyncio
import functools
import json
from typing import TYPE_CHECKING, Any, Dict

import requests
from fake_useragent import FakeUserAgent

if TYPE_CHECKING:
    from requests import Response


class SoundCloud:
    def __init__(self) -> None:
        self.BASE_URL = "https://api-v2.soundcloud.com"
        self.ua = FakeUserAgent().random
        self.session = requests.Session()
        self.headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9,vi;q=0.8",
            "Connection": "keep-alive",
            "Host": "api-v2.soundcloud.com",
            "User-Agent": self.ua,
        }
        self.client_id = "LBCcHmRB8XSStWL6wKH2HPACspQlXg2P"
        self.app_version = "1692966083"

    async def make_request(self, url) -> "Response":
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(
            None, functools.partial(self.session.get, headers=self.headers, url=url)
        )
        response = await future
        return response

    def search(self, query: str):
        search = f"{self.BASE_URL}/search/tracks?q={query}&client_id={self.client_id}&app_version={self.app_version}"
        response = self.session.get(search, headers=self.headers)
        return {
            "total_results": response.json()["total_results"],
            "tracks": response.json()["collection"]
        }

    def resolve_url(self, url: str):
        resolve = f"{self.BASE_URL}/resolve?url={url}&format=json&client_id={self.client_id}&app_version={self.app_version}"
        response = self.session.get(resolve, headers=self.headers)
        return response.json()

    def get_thumbnail(self, track) -> str:
        return track["artwork_url"] or track["user"]["avatar_url"]

    async def get_playback_url(self, track: Dict[str, Any]):
        # Transcoding involves 3 types of protocols: HLS, progressive and Opus.
        # We prefer to use the 'HLS' protocol because it's the best for streaming.
        stream_url = track["media"]["transcodings"][0]["url"]
        track_authorization = track["track_authorization"]
        audio_url = f"{stream_url}?client_id={self.client_id}&track_authorization={track_authorization}"
        response = await self.make_request(audio_url)
        playback_url = response.json()
        return playback_url["url"]

    async def get_playlist_tracks(self, track_ids: list[int], playlist_id: int):
        MAX_TRACKS_PER_REQUEST = 50
        urls = []
        results = []

        if len(track_ids) > MAX_TRACKS_PER_REQUEST:
            chunked_tracks = [
                track_ids[i : i + MAX_TRACKS_PER_REQUEST]
                for i in range(0, len(track_ids), MAX_TRACKS_PER_REQUEST)
            ]
            for chunk in chunked_tracks:
                quoted_track_ids = ",".join(map(str, chunk))
                urls.append(
                    f"{self.BASE_URL}/tracks?ids={quoted_track_ids}&playlistId={playlist_id}&playlistSecretToken&format=json&client_id={self.client_id}"
                )
        else:
            quoted_track_ids = ",".join(map(str, track_ids))
            urls.append(
                f"{self.BASE_URL}/tracks?ids={quoted_track_ids}&playlistId={playlist_id}&playlistSecretToken&format=json&client_id={self.client_id}"
            )

        responses: list[Response] = await asyncio.gather(
            *(self.make_request(url) for url in urls)
        )
        for res in responses:
            results += res.json()

        for i in range(len(track_ids)):
            if track_ids[i] == results[i]["id"]:
                continue
            idx1 = i
            idx2 = [track["id"] for track in results].index(track_ids[i])
            results[idx1], results[idx2] = results[idx2], results[idx1]

        return results

    async def extract_song(self, url: str):
        resolve = self.resolve_url(url)
        if resolve["kind"] == "playlist":
            tracks = resolve["tracks"]
            playlist_id = resolve["id"]
            track_ids = [track["id"] for track in tracks]
            return {
                "playlist_id": playlist_id,
                "playlist_name": resolve["title"],
                "tracks": await self.get_playlist_tracks(track_ids, playlist_id),
            }
        else:
            return {
                "playlist_id": None,
                "playlist_name": None,
                "tracks": [resolve],
            }
