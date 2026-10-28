"""A lazy log-processing pipeline. Replace each stub with a real stage."""
import itertools
from collections.abc import Iterable, Iterator

LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR"]

Record = dict[str, str]


def parse_line(line: str) -> Record | None:
    return None


def parse_lines(lines: Iterable[str]) -> Iterator[Record]:
    yield from ()


def at_least(records: Iterable[Record], min_level: str) -> Iterator[Record]:
    return iter([])


def count_per_minute(records: Iterable[Record]) -> Iterator[tuple[str, int]]:
    yield from ()


def summarize(records: Iterable[Record]) -> dict:
    return {}


def first_messages(lines: Iterable[str], min_level: str, n: int) -> list[str]:
    return []
