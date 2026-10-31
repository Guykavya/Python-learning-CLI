from collections.abc import Callable, Iterable, Iterator


def merge_sorted(*iterables: Iterable[object], key: Callable[[object], object] | None = None) -> Iterator[object]:
    yield from ()
