from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List


class Observer(ABC):
    """
    Abstract base class for observers in the observer pattern.
    Methods:
        update(observable: Observable):
            Asynchronously called to update the observer with changes from the observable.
    """

    @abstractmethod
    async def update(self, observable: Observable) -> None:
        """
        Abstract method to be implemented by subclasses to handle updates from the observable.

        Args:
            observable (Observable): The observable object that notifies the observer of changes.
        """
        pass


class Observable:
    """
    Observable class that maintains a list of observers and notifies them of any changes.
    """

    def __init__(self) -> None:
        self._observers: List[Observer] = []

    def attach(self, observer: Observer) -> None:
        """
        Attaches an observer to the subject.

        Args:
            observer (Observer): The observer to be attached.
        """
        self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        """
        Detaches an observer from the list of observers.

        Args:
            observer (Observer): The observer to be removed from the list.
        """
        self._observers.remove(observer)

    async def notify(self) -> None:
        """
        Asynchronously notifies all observers by calling their update method.

        This method iterates over the list of observers and calls the update method
        on each observer, passing the current instance as an argument.

        Returns:
            None
        """
        for observe in self._observers:
            await observe.update(self)
