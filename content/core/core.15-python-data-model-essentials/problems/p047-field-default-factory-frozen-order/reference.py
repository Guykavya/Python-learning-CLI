from dataclasses import dataclass, field


@dataclass
class Playlist:
    name: str
    songs: list = field(default_factory=list)
    plays: int = field(default=0, repr=False, compare=False)


@dataclass(frozen=True, order=True)
class Version:
    major: int
    minor: int = 0
    patch: int = 0

    def __str__(self):
        return f"{self.major}.{self.minor}.{self.patch}"
