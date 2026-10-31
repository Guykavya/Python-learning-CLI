from collections.abc import Iterable, Iterator


def my_chain(*iterables: Iterable[object]) -> Iterator[object]:
    yield from ()


def my_enumerate(iterable: Iterable[object], start: int = 0) -> Iterator[tuple[int, object]]:
    yield from ()


def my_zip(*iterables: Iterable[object]) -> Iterator[tuple[object, ...]]:
    yield from ()


def my_islice(iterable: Iterable[object], start: int, stop: int | None) -> Iterator[object]:
    yield from ()
