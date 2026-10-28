from collections.abc import Callable, Iterable, Iterator


def merge_sorted(*iterables: Iterable[object], key: Callable[[object], object] | None = None) -> Iterator[object]:
    if key is None:
        key = lambda item: item

    # One entry per input that still has items: [waiting item, its iterator].
    # The list stays in input order, so the first smallest entry is the earliest input.
    waiting = []
    for iterable in iterables:
        it = iter(iterable)
        for item in it:
            waiting.append([item, it])
            break

    while waiting:
        best = 0
        for i in range(1, len(waiting)):
            if key(waiting[i][0]) < key(waiting[best][0]):
                best = i
        item, it = waiting[best]
        yield item
        try:
            waiting[best][0] = next(it)
        except StopIteration:
            waiting.pop(best)
