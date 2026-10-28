from collections.abc import Iterable, Iterator


def my_chain(*iterables: Iterable[object]) -> Iterator[object]:
    for iterable in iterables:
        yield from iterable


def my_enumerate(iterable: Iterable[object], start: int = 0) -> Iterator[tuple[int, object]]:
    index = start
    for item in iterable:
        yield index, item
        index += 1


def my_zip(*iterables: Iterable[object]) -> Iterator[tuple[object, ...]]:
    if not iterables:
        return
    iterators = [iter(x) for x in iterables]
    while True:
        row = []
        for it in iterators:
            try:
                row.append(next(it))
            except StopIteration:
                return
        yield tuple(row)


def my_islice(iterable: Iterable[object], start: int, stop: int | None) -> Iterator[object]:
    if stop is not None and stop <= start:
        return
    position = 0
    for item in iterable:
        if position >= start:
            yield item
        position += 1
        if stop is not None and position >= stop:
            return
