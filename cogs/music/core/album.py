from dataclasses import dataclass


@dataclass(slots=True)
class Album:
    title: str
