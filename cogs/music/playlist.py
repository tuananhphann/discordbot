from collections import deque

from cogs.music.song import Song
from utils import convert_to_second, convert_to_time


class PlayList:
    def __init__(self) -> None:
        self.q = deque()

    def add(self, song: Song) -> None:
        self.q.append(song)

    def add_next(self, song: Song) -> None:
        self.q.appendleft(song)

    def index(self, song: Song) -> int:
        """Index of song in queue."""
        return self.q.index(song)

    def size(self) -> int:
        return len(self.q)

    def clear(self) -> None:
        self.q.clear()

    def time_wait(self) -> str:
        sec = 0
        for i in range(len(self.q)):
            sec += convert_to_second(time=self.q[i].DURATION)
        return convert_to_time(seconds=sec)

    def get_list(self):
        return self.q

    def get_next(self) -> Song:
        try:
            return self.q.popleft()
        except:
            return None
