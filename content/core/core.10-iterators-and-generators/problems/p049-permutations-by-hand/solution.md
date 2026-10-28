## Approach

Recursion on "who goes first". Trying positions from left to right and putting each one in front
of every shorter arrangement of the remaining items gives exactly the order of
`itertools.permutations`. Because every level is a generator, the first answer travels up the
recursion as soon as the deepest call yields it. Nothing waits for the full list.

`anagrams` is a small pipeline on top: arrangements, joined to strings, filtered with a seen set
(the same idea as `unique_by`).

## Code

```python
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
```

## Complexity

There are n! / (n - r)! arrangements, and each costs O(r) to build (tuple and slice copies), so the
total is about O(r * n! / (n - r)!). Memory is only O(r * n) for the paused calls and their `rest` lists.
`anagrams` also stores every different string in the set; for words with many repeated letters most
permutations are thrown away, which is wasteful.

## Another way

A non-recursive version swaps items in a list in place (Heap's algorithm), but it gives a different
order. A smarter `anagrams` avoids duplicates without a set: count the letters with a dict and, at
each level, try each **different** remaining letter once. Then it never builds a repeated string at all.
