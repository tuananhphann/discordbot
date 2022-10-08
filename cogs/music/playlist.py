from collections import deque
from utils import *

class PlayList:
    def __init__(self) -> None:
        self.q = deque()
    
    def add(self, song):
        self.q.append(song)
    
    def add_next(self, song):
        self.q.appendleft(song)
    
    def index(self, song):
        """Index of song in queue."""
        return self.q.index(song)
    
    def size(self):
        return len(self.q)
    
    def clear(self):
        self.q.clear()

    def time_wait(self):
        sec = 0
        for i in range(len(self.q)):
            sec += convert_to_second(self.q[i].DURATION)
        return convert_to_time(sec)
    
    def get_list(self):
        return self.q
    
    def get_next(self):
        try: return self.q.popleft()
        except: return None
