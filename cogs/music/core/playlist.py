import asyncio
import logging
from collections import deque
from typing import Deque, List, Optional, TYPE_CHECKING

from cogs.music.core.song import Song, SongMeta, SoundCloudSongMeta, YouTubeSongMeta, createSong, get_songs_info
from patterns.observe import Observable, Observer
from utils import convert_to_second, convert_to_time

if TYPE_CHECKING:
    from cogs.music.controller import Audio

_logger = logging.getLogger(__name__)

class PlayList(Observable):
    def __init__(self) -> None:
        super().__init__()
        self._q: Deque[SongMeta] = deque()
        self.lock: asyncio.Lock = asyncio.Lock()

    async def add(self, song: SongMeta) -> None:
        """
        Adds a song to the playlist queue and notifies any waiting coroutines.

        Args:
            song (SongMeta): The song metadata to be added to the queue.

        Returns:
            None
        """
        async with self.lock:
            self._q.append(song)
            await self.notify()

    async def add_next(self, song: SongMeta) -> None:
        """
        Adds a song to the front of the playlist queue and notifies any waiting coroutines.

        Args:
            song (SongMeta): The song metadata to be added to the front of the queue.

        Returns:
            None
        """
        async with self.lock:
            self._q.appendleft(song)
            await self.notify()

    def index(self, song: SongMeta) -> Optional[int]:
        """
        Get the index of a song in the queue.

        Args:
            song (SongMeta): The song to find in the queue.

        Returns:
            int | None: The index of the song if found, otherwise None.
        """
        try:
            return self._q.index(song)
        except ValueError:
            return None

    def size(self) -> int:
        """
        Returns the number of items in the playlist.

        Returns:
            int: The number of items in the playlist.
        """
        return len(self._q)

    def empty(self) -> bool:
        """
        Check if the playlist is empty.

        Returns:
            bool: True if the playlist is empty, False otherwise.
        """
        return self.size() == 0

    def clear(self) -> None:
        """
        Clears the playlist queue.

        This method removes all items from the internal playlist queue.
        """
        self._q.clear()

    def time_wait(self, to_song_index: int | None = None) -> str:
        """
        Calculate the total duration of songs in the queue up to a specified index.
        Args:
            to_song_index (int | None): The index up to which the total duration is calculated.
                                        If None, the total duration of all songs in the queue is calculated.
        Returns:
            str: The total duration in a human-readable format (HH:MM:SS).
        """

        if to_song_index is None:
            to_song_index = len(self._q)

        sec = 0
        for i in range(to_song_index):
            sec += convert_to_second(time=self._q[i].duration)

        return convert_to_time(seconds=sec)

    async def get_list(self, limit: int | None = None) -> List[SongMeta]:
        """
        Retrieve a list of songs from the playlist.
        Args:
            limit (int | None, optional): The maximum number of songs to retrieve.
                                          If None, all songs in the playlist are returned. Defaults to None.
        Returns:
            List[SongMeta]: A list of SongMeta objects representing the songs in the playlist.
        """

        if limit is None:
            return [song for song in self._q]
        else:
            return [song for song in list(self._q)[:limit]]

    def get_next(self) -> SongMeta | None:
        """Get the next song meta and remove it from queue

        Returns:
            SongMeta | None
        """
        try:
            return self._q.popleft()
        except IndexError:
            return None

    async def get_next_prepared(self) -> Song | None:
        """
        Asynchronously retrieves the next prepared song.
        This method fetches the next song metadata using the `get_next` method.
        If no metadata is available, it returns None. Otherwise, it attempts to
        create a Song object from the metadata. If the creation fails and there
        are more songs in the playlist, it recursively tries to get the next
        prepared song.
        Returns:
            Song | None: The next prepared Song object, or None if no song is available.
        """

        song_meta = self.get_next()
        if song_meta is None:
            return None

        song_obj = await createSong(song_meta)
        if song_obj is None:
            id = None
            if isinstance(song_meta, YouTubeSongMeta):
                id = song_meta.video_id
            elif isinstance(song_meta, SoundCloudSongMeta):
                id = song_meta.track_id

            _logger.error(
                f"Failed to create song with type: {type(song_meta)}. Title: {song_meta.title}. ID: {id}."
            )
            if self.size() > 0:
                return await self.get_next_prepared()

        return song_obj

    async def __update_all_song_meta(self) -> None:
        """
        Asynchronously updates the metadata for all songs in the queue.
        This method iterates through the song queue and identifies songs that need
        metadata updates (i.e., songs with a `None` title). It then fetches the
        updated metadata for these songs and applies the updates.
        Steps:
        1. Logs the start of the update process.
        2. Collects songs that need metadata updates.
        3. Fetches updated metadata for the collected songs.
        4. Applies the updated metadata to the songs in the queue.
        5. Logs the number of songs that were updated.
        Returns:
            None
        """

        _logger.debug("Updating all song meta info.")
        # Get all songs that need to update meta info. (title is None)
        # Note: None means that the song is not need to update meta info.
        songs_need_to_update = []
        for song in self._q:
            if song.title is None:
                songs_need_to_update.append(song)
            else:
                songs_need_to_update.append(None)

        songs_with_info = await get_songs_info(songs_need_to_update)
        for song, song_with_info in zip(self._q, songs_with_info):
            if song_with_info is not None:
                song = song_with_info
        _logger.debug(
            f"Updated {len([i for i in songs_with_info if i is not None])} song(s) meta info."
        )

    def trigger_update_all_song_meta(self) -> None:
        """
        Trigger update all song meta info.

        This method should be called when a new song is added. It will initiate the
        `__update_all_song_meta` method in the background to update the metadata for
        all songs.

        Returns:
            None
        """
        _logger.debug("Triggering update all song meta info.")
        asyncio.create_task(self.__update_all_song_meta())

class PlaylistObserver(Observer):
    def __init__(self, player: 'Audio') -> None:
        super().__init__()
        self.player = player

    async def update(self, observable: PlayList) -> None:
        await self.player.play_next()