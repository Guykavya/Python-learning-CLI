from collections.abc import Iterable, Iterator


def _perms(pool: list[object], r: int) -> Iterator[tuple[object, ...]]:
    if r == 0:
        yield ()
        return
    for i in range(len(pool)):
        first = pool[i]
        rest = pool[:i] + pool[i + 1:]
        for tail in _perms(rest, r - 1):
            yield (first,) + tail


def perms(items: Iterable[object], r: int | None = None) -> Iterator[tuple[object, ...]]:
    pool = list(items)
    if r is None:
        r = len(pool)
    if r > len(pool):
        return
    yield from _perms(pool, r)


def anagrams(word: str) -> Iterator[str]:
    seen = set()
    for arrangement in perms(word):
        text = "".join(arrangement)
        if text not in seen:
            seen.add(text)
            yield text
