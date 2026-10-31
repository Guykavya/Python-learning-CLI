from collections.abc import Iterable, Iterator


def counted(iterable: Iterable[object]) -> Iterator[object]:
    yield from iterable


def drain(iterator: Iterator[object]) -> tuple[list[object], object]:
    return list(iterator), None
