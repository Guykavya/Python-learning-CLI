import heapq
from collections.abc import Iterable, Iterator
from pathlib import Path


def timestamp(line: str) -> str:
    return line[:19]


def merge_logs(*sources: Iterable[str]) -> Iterator[str]:
    return heapq.merge(*sources, key=timestamp)


def clean_lines(f) -> Iterator[str]:
    for line in f:
        line = line.rstrip("\n")
        if line.strip():
            yield line


def merge_files(paths: list[Path], out_path: Path) -> int:
    files = [open(path, encoding="utf-8") for path in paths]
    try:
        count = 0
        with open(out_path, "w", encoding="utf-8") as out:
            for line in merge_logs(*(clean_lines(f) for f in files)):
                out.write(line + "\n")
                count += 1
    finally:
        for f in files:
            f.close()
    return count
