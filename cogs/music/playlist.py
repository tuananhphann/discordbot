import asyncio
import functools
import inspect
from collections import deque
from dataclasses import fields
from typing import List

from cogs.music.song import Song
from patterns.observe import Observable
from utils.utils import convert_to_second, convert_to_time


class PlayList(Observable):
    def __init__(self) -> None:
        super().__init__()
        self._q = deque()
        self.lock = asyncio.Lock()

    async def add(self, song: Song) -> None:
        async with self.lock:
            self._q.append(song)
            await self.notify()

    async def add_next(self, song: Song) -> None:
        async with self.lock:
            self._q.appendleft(song)
            await self.notify()

    def index(self, song: Song) -> int | None:
        """Index of song in queue."""
        try:
            return self._q.index(song)
        except ValueError:
            return None

    def size(self) -> int:
        return len(self._q)

    def empty(self) -> bool:
        return self.size() == 0

    def clear(self) -> None:
        self._q.clear()

    def time_wait(self, to_song_index: int | None = None) -> str:
        """if to_song_index is None, it will be the length of the playlist"""

        if to_song_index is None:
            to_song_index = len(self._q)

        sec = 0
        for i in range(to_song_index):
            sec += convert_to_second(time=self._q[i].duration)

        return convert_to_time(seconds=sec)

    def get_list(self, limit: int | None = None) -> List[Song]:
        if limit is None:
            return list(self._q)
        else:
            return list(self._q)[:limit]

    def get_next(self) -> Song | None:
        """Get the next song and remove it from queue

        Returns:
            Song | None
        """
        try:
            return self._q.popleft()
        except IndexError:
            return None

    async def get_next_prepared(self) -> Song | None:
        """Beside get_next function, this funtion was created to serve lazy song loading.
        It means, that when the song is loaded, every function that takes time to load
        will be executed instead of loading at its creation time.

        Returns:
            Song | None
        """
        song = self.get_next()
        if song is None:
            return None

        for field in fields(song):
            if isinstance(getattr(song, field.name), tuple):
                params = getattr(song, field.name)[1:]
                callable_f = functools.partial(getattr(song, field.name)[0], *params)
                if inspect.iscoroutinefunction(callable_f):
                    setattr(song, field.name, await callable_f())
                else:
                    setattr(song, field.name, callable_f())
        return song
