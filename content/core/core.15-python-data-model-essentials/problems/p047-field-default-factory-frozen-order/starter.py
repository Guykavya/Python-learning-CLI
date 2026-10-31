from dataclasses import dataclass, field


@dataclass
class Playlist:
    name: str


@dataclass
class Version:
    major: int
    minor: int = 0
    patch: int = 0
