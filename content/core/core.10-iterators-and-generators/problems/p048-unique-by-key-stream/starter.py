from collections.abc import Callable, Hashable, Iterable, Iterator


def unique_by(iterable: Iterable[object], key: Callable[[object], Hashable] | None = None) -> Iterator[object]:
    yield from ()


def new_words(lines: Iterable[str]) -> Iterator[str]:
    yield from ()
