import heapq
from collections.abc import Iterable, Iterator
from pathlib import Path


def merge_logs(*sources: Iterable[str]) -> Iterator[str]:
    return iter([])


def merge_files(paths: list[Path], out_path: Path) -> int:
    return 0
