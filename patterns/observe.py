from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List


class Observer(ABC):

    @abstractmethod
    async def update(self, observable: Observable):
        pass


class Observable:
    def __init__(self) -> None:
        self._observers: List[Observer] = []

    def attach(self, observer: Observer):
        self._observers.append(observer)

    def detach(self, observer: Observer):
        self._observers.remove(observer)

    async def notify(self):
        for observe in self._observers:
            await observe.update(self)
