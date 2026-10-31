from collections.abc import Iterable, Iterator


def counted(iterable: Iterable[object]) -> Iterator[object]:
    n = 0
    for item in iterable:
        n += 1
        yield item
    return n


def drain(iterator: Iterator[object]) -> tuple[list[object], object]:
    items = []
    while True:
        try:
            items.append(next(iterator))
        except StopIteration as e:
            return items, e.value
